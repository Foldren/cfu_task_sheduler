from cryptography.fernet import Fernet
from banks.alfa import Alfa
from banks.module import Module
from banks.tinkoff import Tinkoff
from banks.tochka import Tochka
from config import SECRET_KEY, APP_NAME
from decorators import exception_handler
from db_models.bank import UserBank, PaymentAccount
from modules.logger import Logger


class Balance:
    @staticmethod
    async def __get_bank_rc_balances(user_bank: UserBank) -> dict:
        """
        Функция для подгрузки балансов по расчетным счета банка
        
        :param user_bank: банк, по которому требуется подгрузить балансы UserBank
        :return: значения в формате dict[payment_account_number] = amount
        """

        decrypt_token = Fernet(SECRET_KEY).decrypt(user_bank.token).decode('utf-8')
        support_bank = await user_bank.support_bank
        pa_numbers_list = await user_bank.payment_accounts.all().values_list("number", flat=True)
        balances = {}

        if pa_numbers_list:
            match support_bank.name:
                case 'Тинькофф':
                    balances = await Tinkoff.get_bank_pa_balances(
                        token=decrypt_token,
                        pa_numbers_list=pa_numbers_list
                    )
                case 'Модуль':
                    balances = await Module.get_bank_pa_balances(
                        token=decrypt_token,
                        pa_numbers_list=pa_numbers_list,
                    )
                case 'Точка':
                    balances = await Tochka.get_bank_pa_balances(
                        token=decrypt_token,
                        pa_numbers_list=pa_numbers_list,
                    )
                case 'Альфа':
                    balances = await Alfa.get_bank_pa_balances(
                        token=decrypt_token,
                        pa_numbers_list=pa_numbers_list,
                    )

        return balances

    @exception_handler(app=APP_NAME, func_name="load_balances", msg="Загрузка балансов прервана.")
    async def load(self) -> None:
        """
        Основная функция, для обновления балансов расчетных счетов в бд
        """

        await Logger(APP_NAME).info(msg="Начат процесс подгрузки балансов.", func_name='load_balances')

        users_banks = await UserBank.all()

        pa_balances = {}
        for bank in users_banks:
            try:
                pa_balances = pa_balances | await self.__get_bank_rc_balances(bank)
            except Exception:
                pass

        payment_accounts = await PaymentAccount.filter(number__in=list(pa_balances.keys()))

        for pa in payment_accounts:
            if pa.number in pa_balances.keys():
                pa.balance = pa_balances[pa.number]

        if payment_accounts:
            await PaymentAccount.bulk_update(payment_accounts, fields=['balance'])

        await Logger(APP_NAME).success(msg="Процесс подгрузки балансов завершен.", func_name='load_balances')


