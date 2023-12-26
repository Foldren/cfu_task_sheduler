from datetime import datetime
from traceback import format_exc
from cryptography.fernet import Fernet
from banks.module import Module
from banks.tinkoff import Tinkoff
from banks.tochka import Tochka
from config import SECRET_KEY
from decorators import exception_handler
from models import PaymentAccount, UserBank, DataCollect


class Statement:
    @staticmethod
    async def status_message(status: str):
        match status:
            case 'start_statement_machine':
                print("[message]: The first time the machine is turned on, the first boot will be at 4 a.m o'clock")
            case 'start_load':
                print("[message]: Start load statement")
            case 'end_load':
                print("[message]: Loading statement is complete!")

    @staticmethod
    async def __load_payment_account_statement(payment_account: PaymentAccount) -> list:
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

        # Меняем дату последней подгрузки на сегодня
        payment_account.start_date = datetime.now().date()
        await payment_account.save()

        return statements

    @exception_handler
    async def load(self) -> None:
        """
        Основная функция, для генерации списка строк с операциями data_collect,
        с последующим добавлением в бд

        :return:
        """

        await self.status_message('start_load')

        banks = await UserBank.all()

        data_collects = []
        for bank in banks:
            payment_accounts = await bank.payment_accounts.all()
            support_bank = await bank.support_bank

            for payment_account in payment_accounts:
                try:
                    # Если расчетный счет помечен как активный
                    if payment_account.status == 1:
                        payment_account_stat = await self.__load_payment_account_statement(payment_account)

                        for operation in payment_account_stat:
                            data_collects.append(DataCollect(
                                payment_account_id=payment_account.id,
                                trxn_date=operation['op_date'],
                                counterparty_name=operation['partner_name'],
                                type=operation['op_type'],
                                support_bank_id=support_bank.id,
                                amount=operation['op_volume'],
                                counterparty_inn=operation['partner_inn'],
                            ))
                except Exception:
                    print(format_exc())
                    # continue

        await DataCollect.bulk_create(data_collects, ignore_conflicts=True)
        await self.status_message('end_load')

