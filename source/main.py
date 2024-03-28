from asyncio import get_event_loop
from datetime import datetime
import aiocron
from pytz import timezone
from tortoise import run_async
from config import APP_NAME
from db_models.declaration import Declaration
from init_db import init_db
from modules.balance import Balance
from modules.content_api import ContentApi
from modules.logger import Logger
from modules.statement import Statement


# Запускаем каждые 5 минут
@aiocron.crontab("*/5 * * * *")
async def load_balances():
    await Balance().load()


# Запускаем в 4 утра каждый день
@aiocron.crontab("0 4 * * *", tz=timezone("Europe/Moscow"))
async def load_statements():
    await Statement().load()


# Запускаем каждые 24 часа
@aiocron.crontab("* */24 * * *")
async def delete_incorrect_declaration_notes():
    query = Declaration.filter(status='no_file', date__lte=datetime.now(tz=timezone("Europe/Moscow"))).all()
    inc_declarations = await query

    if inc_declarations:
        for declr in inc_declarations:
            if declr.image_url is not None:
                await ContentApi(declr.user_id).delete(file_url=declr.image_url)

        await query.delete()

        await Logger(APP_NAME).success(msg="Декларации с некорретктной ссылкой удалены.", func_name="delete_incorr_declrs")
    else:
        await Logger(APP_NAME).info(msg="У всех деклараций корректная ссылка.", func_name="delete_incorr_declrs")


if __name__ == '__main__':
    loop = get_event_loop()
    loop.run_until_complete(Logger(APP_NAME).success(msg="Планировщик запущен.", func_name="startup"))

    run_async(init_db())
    get_event_loop().run_forever()
