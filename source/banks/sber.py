# from datetime import datetime
# from httpx import AsyncClient
# from config import PROXY6NET_PROXIES, APP_NAME
# from modules.logger import Logger
#
#
# class Sber:
#     @staticmethod
#     async def get_bank_pa_balances(token: str, pa_numbers_list: list[str]):
#         """
#         Функция для получения балансов по выбранным расчетным счетам
#         :param token: токен Альфа банка
#         :param pa_numbers_list: номера счетов
#         :return: объект dict[pa_number, pa_balance]
#         """
#
#         headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/json'}
#         url_operation = 'https://baas.alfabank.ru/api/pp/v1/accounts'
#
#         async with AsyncClient(proxies=PROXY6NET_PROXIES) as async_session:
#             r_balances = await async_session.get(
#                 url=url_operation,
#                 headers=headers
#             )
#
#         accounts = r_balances.json()['accounts']
#
#         pa_balances = {}
#         for pa in accounts:
#             if pa['number'] in pa_numbers_list:
#                 pa_balances[pa['number']] += pa['balance']['amount']
#
#         return pa_balances
#
#     @staticmethod
#     async def get_statement(token: str, rc_number: int, from_date: str) -> list:
#         """
#         Функция для получения выписок по счету в Альфа банке от заданной даты до текущего времени
#
#         :param token: токен клиентского Альфа банка
#         :param rc_number: номер расчетного счета клиента
#         :param from_date: дата начала периода отгрузки выписки (в формате 2023-07-13)
#         :return:
#         """
#
#         from_date_frmt = f'{from_date}T00:00:00Z'
#         headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/json'}
#         url_operation = 'https://baas.alfabank.ru/api/pp/v1/operations'
#
#         # Получаем выписки, делаем это со смещением даты пока не выведем все -------------------------------------------
#         result_operations_list = []
#         till_date_frmt = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
#         last_operations = []
#         while True:
#             async with AsyncClient(proxies=PROXY6NET_PROXIES) as async_session:
#                 r_operations = await async_session.get(
#                     url=url_operation,
#                     headers=headers,
#                     params={
#                         'accounts': [rc_number],
#                         'limit': 10000,
#                         'dateFrom': str(from_date_frmt),
#                         'dateTo': str(till_date_frmt),
#                     }
#                 )
#
#             if r_operations.status_code != 200:
#                 await Logger(APP_NAME).error(msg="Ошибка при подгрузке выписок Альфа банка.", func_name="get_statement")
#                 raise Exception
#
#             r_operations_list = r_operations.json()['operations']
#
#             if (last_operations == r_operations_list) or (not r_operations_list):
#                 break
#
#             index_last_operation = len(r_operations_list) - 1
#             from_date_frmt = str(r_operations_list[index_last_operation]['dateTime'])
#             result_operations_list += r_operations_list
#             last_operations = r_operations_list
#
#         # Получаем транзакции  -----------------------------------------------------------------------------------------
#         result_data_list = []
#         for operation in result_operations_list:
#             cp_name = operation['sender']["name"]
#             cp_inn = operation['sender']["accountNumber"]
#             type_operation = "Расход" if operation["direction"] == "EXPENSE" else "Доход"
#             volume_operation = operation["amount"]
#             trxn_date = datetime.strptime(operation["dateTime"], '%Y-%m-%dT%H:%M:%SZ')
#             result_data_list.append({
#                 'partner_inn': cp_inn,
#                 'partner_name': cp_name,
#                 'op_volume': volume_operation if type_operation == "Доход" else -round(volume_operation, 2),
#                 'op_type': type_operation,
#                 'op_date': trxn_date,
#                 'op_id': operation['id'],
#             })
#
#         return result_data_list
