from cryptography.fernet import Fernet
from banks.module import Module
from banks.tinkoff import Tinkoff
from banks.tochka import Tochka
from config import SECRET_KEY
from decorators import exception_handler
from db_models.bank import UserBank, PaymentAccount


class Balance:
    @staticmethod
    async def status_message(status: str):
        match status:
            case 'start':
                print("[message]: Start update balances")
            case 'end':
                print("[message]: Updating balances is complete!")

    @staticmethod
    async def __get_bank_rc_balances(user_bank: UserBank) -> dict:
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

        return balances

    @exception_handler
    async def load(self) -> None:
        """
        Основная функция, для обновления балансов расчетных счетов в бд

        """
        await self.status_message("start")

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

        await self.status_message("end")


