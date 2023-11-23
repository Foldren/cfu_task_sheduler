from datetime import datetime
from httpx import AsyncClient
from config import PROXY6NET_PROXIES


class TinkoffBank:
    @staticmethod
    async def get_statement(token: str, rc_number: int, from_date: str) -> list:
        """
        Функция для получения выписок по счету в Тинькофф от заданной даты до текущего времени

        :param token: токен клиентского Тинькофф
        :param rc_number: номер расчетного счета клиента
        :param from_date: дата начала периода отгрузки выписки (в формате 2023-07-13)
        :return:
        """

        from_date_frmt = f'{from_date}T00:00:00Z'
        headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
        url_operation = 'https://business.tinkoff.ru/openapi/api/v1/statement'

        # Получаем выписки, так как ограничение стоит на 5000 делаем это со смещением даты пока не выведем все ---------
        result_operations_list = []
        till_date_frmt = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        last_operations = []
        while True:
            r_operations = await AsyncClient(proxies=PROXY6NET_PROXIES).get(
                url=url_operation,
                headers=headers,
                params={
                    'accountNumber': rc_number,
                    'limit': 5000,
                    'from': str(from_date_frmt),
                    'to': str(till_date_frmt),
                    'operationStatus': ['Transaction'],
                }
            )

            if r_operations.status_code != 200:
                raise Exception(f"[error]: ERROR ON API TINKOFF:\n\n {r_operations.text}")

            r_operations_list = r_operations.json()['operations']

            if (last_operations == r_operations_list) or (not r_operations_list):
                break

            index_last_operation = len(r_operations_list) - 1
            from_date_frmt = str(r_operations_list[index_last_operation]['trxnPostDate'])
            result_operations_list += r_operations_list
            last_operations = r_operations_list

        # Получаем транзакции  -----------------------------------------------------------------------------------------
        result_data_list = []
        for operation in result_operations_list:
            cp_name = operation['counterParty']["name"]
            cp_inn = operation['counterParty']["inn"]
            type_operation = "Расход" if operation["typeOfOperation"] == "Debit" else "Доход"
            volume_operation = operation["operationAmount"]
            trxn_date = datetime.strptime(operation["trxnPostDate"], '%Y-%m-%dT%H:%M:%SZ')
            result_data_list.append({
                'partner_inn': cp_inn,
                'partner_name': cp_name,
                'op_volume': volume_operation if type_operation == "Доход" else -round(volume_operation, 2),
                'op_type': type_operation,
                'op_date': trxn_date,
            })

        return result_data_list
