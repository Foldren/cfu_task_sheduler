from asyncio import run
from datetime import datetime
from cryptography.fernet import Fernet
from tortoise import run_async
from banks.alfa import Alfa
from banks.module import Module
from banks.sber import Sber
from banks.tinkoff import Tinkoff
from banks.tochka import Tochka
from config import SECRET_KEY, APP_NAME
from db_models.telegram import Counterparty
from decorators import exception_handler
from db_models.bank import PaymentAccount, UserBank, DataCollect
from init_db import init_db
from modules.logger import Logger


class Statement:
    @staticmethod
    async def __load_payment_account_statement(payment_account: PaymentAccount) -> list[dict]:
        """
        Метод подгрузки выписок по расчетному счету
        :param payment_account: объект PaymentAccount
        :return: объект list[dict_item]

        dict_item = {'partner_inn': ИНН контрагента,
                     'partner_name': имя контрагента,\n
                     'op_volume': объем операции в рублях,\n
                     'op_type': тип операции Доход/Расход,\n
                     'op_date': дата операции,\n
                     'op_id': id транзакции
                     }
        """

        bank = await payment_account.user_bank.first().select_related('support_bank')
        decrypt_token = Fernet(SECRET_KEY).decrypt(bank.token).decode('utf-8')

        # Фиксируем дату, с которой нужно начать подгрузку операций из выписок
        from_date = payment_account.start_date

        statements = None
        match bank.support_bank.name:
            case 'Тинькофф':
                statements = await Tinkoff.get_statement(
                    token=decrypt_token,
                    rc_number=payment_account.number,
                    from_date=from_date,
                )
            case 'Модуль':
                statements = await Module.get_statement(
                    token=decrypt_token,
                    rc_number=payment_account.number,
                    from_date=from_date,
                )
            case 'Точка':
                statements = await Tochka.get_statement(
                    token=decrypt_token,
                    rc_number=payment_account.number,
                    from_date=from_date,
                )
            case 'Альфа':
                statements = await Alfa.get_statement(
                    token=decrypt_token,
                    rc_number=payment_account.number,
                    from_date=from_date,
                )

        # Меняем дату последней подгрузки на сегодня
        payment_account.start_date = datetime.now().date()
        await payment_account.save()

        return statements

    @exception_handler(app=APP_NAME, func_name="load_email_statement", msg="Подгрузка выписок с почты прервана.")
    async def load_with_balances_from_emails(self) -> None:
        """
        Функция, для генерации списка строк с операциями data_collect,
        с последующим добавлением в бд (подгрузка с почты), а также обновлением балансов через почту (на данный момент
        только Сбер)
        """

        await Logger(APP_NAME).info(msg="Начат процесс подрузки выписок с почты.", func_name="load_email_statement")

        try:
            banks = await UserBank.filter(support_bank_id=6).all()  # Берем банки по Сберу
        except TypeError:
            await Logger(APP_NAME).error(msg="Подгрузка выписок не завершена, в базе нет ниодного банка.",
                                         func_name="load_email_statement")
            return

        data_collects = []
        new_counterparties = []
        pa_sber_credentials = await Sber.get_pa_credentials_from_email()

        for bank in banks:
            # По полученным с почты счетам берем данные из бд
            payment_accounts = await bank.payment_accounts.filter(number__in=pa_sber_credentials.keys()).all()
            user_counterparties_inn = await Counterparty.filter(user_id=bank.user_id).values_list("inn", flat=True)

            for payment_account in payment_accounts:
                try:
                    if pa_sber_credentials[payment_account.number]['balance'] is not None:
                        payment_account.balance = str(pa_sber_credentials[payment_account.number]['balance'])

                    if ((payment_account.start_date <= pa_sber_credentials[payment_account.number]['date']) and
                            (payment_account.status == 1)):
                        payment_account.start_date = datetime.now().date()
                        for operation in pa_sber_credentials[payment_account.number]['statements']:
                            data_collects.append(DataCollect(
                                payment_account_id=payment_account.id,
                                trxn_id=operation['op_id'],
                                trxn_date=operation['op_date'],
                                counterparty_name=operation['partner_name'][:99],
                                type=operation['op_type'],
                                support_bank_id=bank.support_bank_id,
                                amount=operation['op_volume'],
                                counterparty_inn=operation['partner_inn'],
                            ))

                            # Если ИНН контрагента новый для этого юзера, то добавляем его в список на создание
                            if operation['partner_inn'] not in user_counterparties_inn:
                                new_counterparties.append(Counterparty(user_id=bank.user_id,
                                                                       inn=operation['partner_inn'],
                                                                       name=operation['partner_name'][:99]))
                                user_counterparties_inn.append(operation['partner_inn'])
                    await payment_account.save()

                except Exception as e:
                    await Logger(APP_NAME).error(msg=f"Невозможно подгрузить выписки по данному счету. Ошибка: {e}",
                                                 func_name="load_statement")

        # Создаем контрагентов
        await Counterparty.bulk_create(new_counterparties, ignore_conflicts=True)
        await DataCollect.bulk_create(data_collects, ignore_conflicts=True)
        await Logger(APP_NAME).info(msg="Процесс подрузки выписок с почты завершен.", func_name="load_email_statement")

    @exception_handler(app=APP_NAME, func_name="load_statement", msg="Подгрузка выписок прервана.")
    async def load(self) -> None:
        """
        Основная функция, для генерации списка строк с операциями data_collect,
        с последующим добавлением в бд
        """

        await Logger(APP_NAME).info(msg="Начат процесс подрузки выписок.", func_name="load_statement")

        try:
            banks = await UserBank.all()
        except TypeError:
            await Logger(APP_NAME).error(msg="Подгрузка выписок не завершена, в базе нет ниодного банка.",
                                         func_name="load_statement")
            return

        new_counterparties = []
        data_collects = []
        for bank in banks:
            payment_accounts = await bank.payment_accounts.all()
            support_bank = await bank.support_bank
            user_counterparties_inn = await Counterparty.filter(user_id=bank.user_id).values_list("inn", flat=True)

            for payment_account in payment_accounts:
                try:
                    # Если расчетный счет помечен как активный
                    if payment_account.status == 1:
                        payment_account_stat = await self.__load_payment_account_statement(payment_account)

                        for operation in payment_account_stat:
                            data_collects.append(DataCollect(
                                payment_account_id=payment_account.id,
                                trxn_id=operation['op_id'],
                                trxn_date=operation['op_date'],
                                counterparty_name=operation['partner_name'],
                                type=operation['op_type'],
                                support_bank_id=support_bank.id,
                                amount=operation['op_volume'],
                                counterparty_inn=operation['partner_inn'],
                            ))

                            # Если ИНН контрагента новый для этого юзера, то добавляем его в список на создание
                            if operation['partner_inn'] not in user_counterparties_inn:
                                new_counterparties.append(Counterparty(user_id=bank.user_id,
                                                                       inn=operation['partner_inn'],
                                                                       name=operation['partner_name']))
                                user_counterparties_inn.append(operation['partner_inn'])

                except Exception as e:
                    await Logger(APP_NAME).error(msg=f"Невозможно подгрузить выписки по данному счету. Ошибка: {e}",
                                                 func_name="load_statement")

        # Создаем контрагентов
        await Counterparty.bulk_create(new_counterparties, ignore_conflicts=True)
        await DataCollect.bulk_create(data_collects, ignore_conflicts=True)
        await Logger(APP_NAME).info(msg="Процесс подрузки выписок завершен.", func_name="load_statement")


if __name__ == "__main__":
    run_async(init_db())
    run(Statement().load_with_balances_from_emails())
