from asyncio import run
from datetime import datetime, timedelta
from typing import Any
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from httpx import AsyncClient, ConnectTimeout
from imap_tools import MailBox, AND, OR, A, O
from config import PROXY6NET_PROXIES, MAIL_PASSW, MAIL_LOGIN


class Sber:
    @staticmethod
    async def get_pa_credentials_from_email() -> dict[str, Any]:
        """
        Функция для получения доступных выписок со счетов, включая балансы счетов в Сбербанке (с датой начиная от
        datetime.now() - timedelta(days=3))

        :return:
        """

        pa_credentials = {}

        with MailBox(host="imap.mail.ru", port=993).login(username=MAIL_LOGIN, password=MAIL_PASSW) as inbox:
            # В запросе берем месседжы только с 2 почт + датой не позднее (сегодняшняя дата - 3 дня)
            query = AND(
                OR(
                    O(from_='k.demchenko@cfunalog.ru'),
                    O(from_='SberBusiness@sberbank.ru'),
                    O(from_='sbbol@sberbank.ru'),
                    ),
                A(date_gte=(datetime.now() - timedelta(days=3)).date())
            )

            all_inbox_messages = inbox.fetch(query)

            for message in all_inbox_messages:
                msg_html_obj = BeautifulSoup(message.html, features="html.parser")

                # Берем объект html со ссылкой на скачку
                download_obj = msg_html_obj.find(string="Скачать отчёт")

                if download_obj is None:
                    url_download_st = msg_html_obj.find(string="Скачать выписку").parent.attrs['href']
                    pa_number = msg_html_obj.find(string="Счёт").next.text
                    html_date_operations = msg_html_obj.find(string="Период").next.text.split(" - ")[0]
                else:
                    url_download_st = download_obj.parent.attrs['href']
                    pa_number = msg_html_obj.find(string="Счет:").next.text
                    html_date_operations = msg_html_obj.find(string="Период:").next.text.split(" — ")[0]

                date_operations = datetime.strptime(html_date_operations, '%d.%m.%Y')

                # Создаем список выписок для расчетного счета по указанной дате
                if pa_number not in pa_credentials:
                    pa_credentials[pa_number] = {'date': date_operations, 'balance': 0.0, 'statements': []}

                try:
                    async with AsyncClient(proxies=PROXY6NET_PROXIES, verify=False) as async_session:
                        r_download_st = await async_session.get(
                            # https://www.dropbox.com/scl/fi/jrdvhnfar0nggz4iueb0g/zip_test-8.zip?rlkey=rcuug4v5p1bpscu2seapbl73t&dl=1
                            # https://www.dropbox.com/scl/fi/at3f7tyhvnpi2vcbpyjat/v8_D805_269.txt?rlkey=qbap6ooupsjty439dnlwjhan5&dl=1
                            url=url_download_st,
                            follow_redirects=True,
                            headers={'User-Agent': UserAgent().random}, timeout=4)

                    # Если ссылка больше не активна
                    if r_download_st.status_code == 302:
                        continue

                except ConnectTimeout:
                    continue

                i = -1
                # Читаем файл и фиксируем выписки
                try:
                    # Распаковываем архив и читаем первый файл
                    # with ZipFile(file=BytesIO(r_download_st.content)) as zip_obj:
                    #     # Берем первый файл из архива
                    #     fst_zip_filename = zip_obj.infolist()[0].filename
                    #     statement_list_params = zip_obj.read(fst_zip_filename).decode('windows-1251').split("\n")

                    statement_list_params = r_download_st.content.decode('windows-1251').split("\n")

                    for param in statement_list_params:
                        param = param.replace("\r", "")
                        param_id_val = param.split("=")

                        if param_id_val[0] == "КонечныйОстаток":
                            pa_credentials[pa_number]['balance'] = float(param_id_val[1])

                        if param_id_val[0] == "Номер":
                            i += 1
                            pa_credentials[pa_number]['statements'].append({'op_id': param_id_val[1]})
                            continue

                        elif param_id_val[0] == "ПлательщикИНН":
                            pa_credentials[pa_number]['statements'][i]['partner_inn'] = param_id_val[1]

                        elif param_id_val[0] == "Плательщик":
                            pa_credentials[pa_number]['statements'][i]['partner_name'] = param_id_val[1]

                        elif param_id_val[0] == "ДатаПоступило":
                            if param_id_val[1]:
                                pa_credentials[pa_number]['statements'][i]['op_type'] = "Доход"
                            else:
                                pa_credentials[pa_number]['statements'][i]['op_type'] = "Расход"

                        elif param_id_val[0] == "Дата":
                            pa_credentials[pa_number]['statements'][i]['op_date'] = datetime.strptime(param_id_val[1],
                                                                                                  '%d.%m.%Y')

                        elif param_id_val[0] == "Сумма":
                            pa_credentials[pa_number]['statements'][i]['op_volume'] = param_id_val[1]

                except Exception:
                    pass

        return pa_credentials
