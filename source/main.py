from asyncio import create_task, run
from rocketry import Rocketry
from rocketry.conds import daily, every
from tortoise import run_async
from init_db import init_db
from modules.balance import Balance
from modules.statement import Statement

app = Rocketry(execution="async")


@app.task(daily.between("04:00", "04:01"))
async def load_statements():
    statement = Statement()
    await statement.load()


@app.task(every("10 sec"))
async def load_balances():
    balance = Balance()
    await balance.status_message("start")
    await balance.load()
    await balance.status_message("end")


async def main():
    await Statement.status_message('start_statement_machine')
    rocketry_task = create_task(app.serve())
    await rocketry_task


if __name__ == '__main__':
    run_async(init_db())
    run(main())
