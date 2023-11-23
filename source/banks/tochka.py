from asyncio import sleep
from datetime import datetime
from httpx import AsyncClient
from config import PROXY6NET_PROXIES


class TochkaBank:
    @staticmethod
    async def get_statement(token: str, rc_number: int, from_date: str) -> list[dict]:
        """
        Функция для получения выписок по счету в Точка банке от заданной даты до текущего времени

        @param token: токен клиентского Точка банка
        @param rc_number: номер расчетного счета клиента
        @param from_date: дата начала периода отгрузки выписки (в формате 2023-07-13)
        @return: list[dict]
        """

        headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
        url_operation = 'https://enter.tochka.com/uapi/open-banking/v1.0/accounts'

        async with AsyncClient(proxies=PROXY6NET_PROXIES) as async_session:
            # Получаем информацию о компании ---------------------------------------------------------------------------
            r_company_info = await async_session.get(
                url=url_operation,
                headers=headers
            )

            if r_company_info.status_code != 200:
                raise Exception(f"[error]: ERROR ON API TOCHKA:\n\n {r_company_info.text}")

            r_company_accounts = r_company_info.json()['Data']['Account']
            account_id = ""

            # Берем account_id по указанному расчётному счёту ----------------------------------------------------------
            for a in r_company_accounts:
                if a['accountId'].split("/")[0] == str(rc_number):
                    account_id = a['accountId']
                    break

            # Создаем выписку за требуемый период ----------------------------------------------------------------------
            r_company_init_statement = await async_session.post(
                url="https://enter.tochka.com/uapi/open-banking/v1.0/statements",
                headers=headers,
                json={
                    'Data': {
                        'Statement': {
                            'accountId': account_id,
                            'startDateTime': str(from_date),
                            'endDateTime': str(datetime.now().strftime("%Y-%m-%d")),
                        }
                    },
                }
            )

            # Выводим созданную выписку --------------------------------------------------------------------------------
            statement_id = r_company_init_statement.json()['Data']['Statement']['statementId']
            url_operation = f"https://enter.tochka.com/uapi/open-banking/v1.0/accounts/{account_id}" \
                            f"/statements/{statement_id}"
            await sleep(2)
            while True:
                try:
                    r_company_get_statement = await async_session.get(url=url_operation, headers=headers)
                    rcgs_json = r_company_get_statement.json()
                    if rcgs_json['Data']['Statement'][0]['status'] == 'Ready':
                        break
                except:
                    await sleep(0.5)

            result_operations_list = r_company_get_statement.json()['Data']['Statement'][0]['Transaction']

        # Получаем транзакции  -----------------------------------------------------------------------------------------
        result_data_list = []
        for operation in result_operations_list:
            if 'CreditorParty' in operation:
                creditor_party = operation['CreditorParty']
                cp_name = creditor_party["name"]
                if 'inn' in creditor_party:
                    cp_inn = creditor_party["inn"]
                else:
                    cp_inn = ""

            else:  # DebtorParty
                debtor_party = operation['DebtorParty']
                cp_name = debtor_party["name"]
                if 'inn' in debtor_party:
                    cp_inn = debtor_party["inn"]
                else:
                    cp_inn = ""

            type_operation = "Расход" if operation["creditDebitIndicator"] == "Debit" else "Доход"
            volume_operation = operation["Amount"]["amount"]
            trxn_date = datetime.strptime(operation["documentProcessDate"], '%Y-%m-%d')
            result_data_list.append({
                'partner_inn': cp_inn,
                'partner_name': cp_name,
                'op_volume': volume_operation if type_operation == "Доход" else -round(volume_operation, 2),
                'op_type': type_operation,
                'op_date': trxn_date,
            })

        return result_data_list
