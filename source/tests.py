from asyncio import run

from banks.module import Module
from banks.tinkoff import Tinkoff

# if __name__ == "__main__":
    # run(Tinkoff.get_statement(
    #     api_key="t.qCm87E5ocCY4ziCoXaHQQMQ-NPLdmYmWueSTdPranxqPp4YbnJnFKtmGh7rYKoGmJxHIqP9yJMB9NLqxvTHe6A",
    #     rc_number=40802810100002730336,
    #     from_date="2023-01-01"))
    # run(Tinkoff.get_overall_balance(token="t.qCm87E5ocCY4ziCoXaHQQMQ-NPLdmYmWueSTdPranxqPp4YbnJnFKtmGh7rYKoGmJxHIqP9yJMB9NLqxvTHe6A", rc_numbers_list=['40802810200001983563']))
# from banks.tochka import Tochka
#
# if __name__ == "__main__":
#     run(Tochka.get_bank_pa_balances(
#         token='eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJUOWxiMlJoOFVjaFBoZWlvOUxzRjF2eWpNeXJaN3YxRyJ9.kX2lBukqa1IBPjlP4qzjs0U45Hspfg8Tg8I-QuffDome_VmtfyPv4hA0GENixs2JGMuerAmEM8iOzmeHeVedhcizEB72UWfB3OYugd8FAT36r3stOOF74EU3em9N-iSEJVJI5NfjoUkc7S1QpLhPdDB1ltYGHb1HUNFiprSPf2WKUdwA0hDkXJsBdq2_fPVR6domf6ZTBylC3pC7HDsQWuP5ab38sMUjxyZ2OF-3DDjO5AeP-nU54M_l82RF43sjm-FUkhdBoVmruOLnqTBg6jDmY7mroNfBWM12i7i7D-OgCnmD9wKWzflSh-Pp-_v46f62LhAqpXlWHxaL2XRyDCjCVOixwYPIHbMdSUCp66kVyaT237yAUEwKedo2Dh5mkD0G16Ylwz-kP1uAxce-xpd1-CJqW-ln1lnres39qPfwyY-HXd9siv68-T4cGkf22LXiWAECrs-RXNiFSFlXQmCq4PxqNBWI_gNf9n_sDzE98HN2BWG_VLWT7lHzgY9e',
#         pa_numbers_list=["40802810014500047652"],
#     ))

from models import UserBank
from modules.balance import Balance

# if __name__ == "__main__":
    # run(ModuleBank.get_statement(
    #     api_key="NTU1OTY4ZDMtN2EyYi00ZTM0LWI1ZmQtOTVlNWFlMDcwNDUwMzNhYmU0YTgtNjUxZi00MTNjLTlkNjAtOWU0ODMwMGMyNjM3",
    #     rc_number=40802810070010406912,
    #     from_date="2023-01-01"))

    # run(Module.get_bank_pa_balances(token="NTU1OTY4ZDMtN2EyYi00ZTM0LWI1ZmQtOTVlNWFlMDcwNDUwMzNhYmU0YTgtNjUxZi00MTNjLTlkNjAtOWU0ODMwMGMyNjM3", pa_numbers_list=['40802810070010406912']))
    # run(Balance.get())