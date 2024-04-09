from asyncio import run

from banks.module import Module
from banks.tinkoff import Tinkoff
from banks.tochka import Tochka

# if __name__ == "__main__":
    # run(Tinkoff.get_statement(
    #     api_key="t.qCm87E5ocCY4ziCoXaHQQMQ-NPLdmYmWueSTdPranxqPp4YbnJnFKtmGh7rYKoGmJxHIqP9yJMB9NLqxvTHe6A",
    #     rc_number=40802810100002730336,
    #     from_date="2023-01-01"))
    # run(Tinkoff.get_overall_balance(token="t.qCm87E5ocCY4ziCoXaHQQMQ-NPLdmYmWueSTdPranxqPp4YbnJnFKtmGh7rYKoGmJxHIqP9yJMB9NLqxvTHe6A", rc_numbers_list=['40802810200001983563']))
# from banks.tochka import Tochka
#

# if __name__ == "__main__":
#     print(run(Tochka.get_bank_pa_balances(
#         token='eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJQQW1NR3RZSHF4S1NTdUlkM1BLenYxdGxLNFh1bDJwOCJ9.eDGdFpu8g9FKg6rhQJ4JyoYNyrJTyvkOlqfT20NP9m4A4hV-hgGcWBe8HQ_TtVfAottECciDRoGLyHqtPXvxVzPuj2XPwPc2SrLp_Sp8n6tHXa08v9aFoIiXA1na-CqohcI7KfcPkoHIddseVLhVINhKqhoRIg6yO3U0iSK4Da_0DipZjSMY669oqTKuACp9cDymrec6zYwsMc_RfPcrJwwwEFWIP6GoMPCC0JOq3U837qHtmh3MjYzg0D0G0Ub4ybNPVmcuBgceTteLhH64xhcnIyJQq2kIcaRzfIKvUBGo24V9ywxrldB7fPZjhk4g_Sh_staOI0C8UX4KPdSodGeO76L8n8DbJIhjFOhKMhrG76d8aVbPRzNmUBOYybmW1DJfUojzM_ZN-q7k1dPvJIQt-nEaMXOocQHWxhSgFKlEBabZHmfYRh48UmtcotbMPV4HIUgHj3zaKUzhVj1t2KSWyfngEXUN5qmvlVXPqJJo-fTYy52LmWlqmupycCFh',
#         pa_numbers_list=["40802810520000021154"],
#     )))

# if __name__ == "__main__":
#     print(run(Tochka.get_statement(
#         token='eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJQQW1NR3RZSHF4S1NTdUlkM1BLenYxdGxLNFh1bDJwOCJ9.eDGdFpu8g9FKg6rhQJ4JyoYNyrJTyvkOlqfT20NP9m4A4hV-hgGcWBe8HQ_TtVfAottECciDRoGLyHqtPXvxVzPuj2XPwPc2SrLp_Sp8n6tHXa08v9aFoIiXA1na-CqohcI7KfcPkoHIddseVLhVINhKqhoRIg6yO3U0iSK4Da_0DipZjSMY669oqTKuACp9cDymrec6zYwsMc_RfPcrJwwwEFWIP6GoMPCC0JOq3U837qHtmh3MjYzg0D0G0Ub4ybNPVmcuBgceTteLhH64xhcnIyJQq2kIcaRzfIKvUBGo24V9ywxrldB7fPZjhk4g_Sh_staOI0C8UX4KPdSodGeO76L8n8DbJIhjFOhKMhrG76d8aVbPRzNmUBOYybmW1DJfUojzM_ZN-q7k1dPvJIQt-nEaMXOocQHWxhSgFKlEBabZHmfYRh48UmtcotbMPV4HIUgHj3zaKUzhVj1t2KSWyfngEXUN5qmvlVXPqJJo-fTYy52LmWlqmupycCFh',
#         rc_number=40802810520000021154,
#         from_date="2024-01-13"
#     )))

# from models import UserBank
# from modules.balance import Balance

# if __name__ == "__main__":
#     print(run(Module.get_bank_pa_balances(
#         token="MWM3MGZiY2UtOTQ5Yi00MzZhLTg0ZDItYmEyYzg1NGJjOTk0NzFiNTk1NzUtOGM4MS00ZWQzLWE4MWItNjRmY2UyMGJiM2My",
#         pa_numbers_list=["40802810970010181793"])))

    # run(Module.get_bank_pa_balances(token="NTU1OTY4ZDMtN2EyYi00ZTM0LWI1ZmQtOTVlNWFlMDcwNDUwMzNhYmU0YTgtNjUxZi00MTNjLTlkNjAtOWU0ODMwMGMyNjM3", pa_numbers_list=['40802810070010406912']))
    # run(Balance.get())