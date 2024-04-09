from asyncio import run
from io import BytesIO
from json import dumps
from zipfile import ZipFile
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from httpx import AsyncClient
from imbox import Imbox
from config import PROXY6NET_PROXIES, SBER_MAIL_PASSW, SBER_MAIL_LOGIN, IMAP_SERVER


class Sber:
    @staticmethod
    async def get_statement_from_email() -> list:
        """
        Функция для получения доступных выписок по счету в Сбербанке от заданной даты до текущего времени

        :param rc_number: номер расчетного счета клиента
        :param from_date: дата начала периода отгрузки выписки (в формате 2023-07-13)
        :return:
        """

        with Imbox(hostname=IMAP_SERVER,
                   port=993,
                   username=SBER_MAIL_LOGIN,
                   password=SBER_MAIL_PASSW,
                   ssl=True) as imbox:

            all_inbox_messages = imbox.messages(sent_from='k.demchenko@cfunalog.ru')

            for uid, message in all_inbox_messages:
                msg_html_obj = BeautifulSoup(message.body['html'][0], features="html.parser")

                # Берем из кнопки ссылку на скачку
                url_download_st = msg_html_obj.find(string="Скачать отчёт").parent.attrs['href']
                async with AsyncClient(proxies=PROXY6NET_PROXIES, verify=False) as async_session:
                    r_download_st = await async_session.get(url="https://www.dropbox.com/scl/fi/jrdvhnfar0nggz4iueb0g/zip_test-8.zip?rlkey=rcuug4v5p1bpscu2seapbl73t&dl=1",
                                                            follow_redirects=True,
                                                            headers={'User-Agent': UserAgent().random}, timeout=2)

                # Если ссылка больше не активна
                if r_download_st.status_code == 302:
                    continue

                zip_statement = r_download_st.content
                statements = []
                # Распаковываем архив и читаем первый файл
                with ZipFile(file=BytesIO(zip_statement)) as zip_obj:
                    fst_zip_filename = zip_obj.infolist()[2].filename
                    statement_list_params = zip_obj.read(fst_zip_filename).decode('windows-1251').split("\n")

                    for param in statement_list_params:
                        param = param.replace("\r", "")
                        param_id_val = param.split("=")

                        # if param_id_val[0] == "Получатель":
                        # statement_frmt_list_data[param_id_val[0]] = param_id_val[1] if len(param_id_val) > 1 else ""

                    print(statement_list_params)

                    # 'partner_inn': cp_inn,
                    # 'partner_name': cp_name,
                    # 'op_volume': volume_operation,
                    # 'op_type': type_operation,
                    # 'op_date': trxn_date,
                    # 'op_id': operation['id'],

                    # except Exception:
                    #     pass



if __name__ == '__main__':
    run(Sber.get_statement_from_email())
