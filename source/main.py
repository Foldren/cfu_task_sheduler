from os import system
from taskiq import TaskiqScheduler, InMemoryBroker
from taskiq.schedule_sources import LabelScheduleSource
from tortoise import run_async
from init_db import init_db
from modules.balance import Balance
from modules.statement import Statement


broker = InMemoryBroker()
scheduler = TaskiqScheduler(broker=broker, sources=[LabelScheduleSource(broker)])


# Запускаем каждые 5 минут
@broker.task(schedule=[{"cron": "*/5 * * * *"}])
async def load_balances():
    await Balance().load()


# Запускаем в 4 утра каждый день
@broker.task(schedule=[{"cron": "0 4 * * *", "cron_offset": "Europe/Moscow"}])
async def load_statements():
    await Statement().load()


if __name__ == '__main__':
    run_async(init_db())
    system("taskiq scheduler --skip-first-run main:scheduler")

