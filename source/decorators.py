from modules.logger import Logger


def exception_handler(app: str, func_name: str, msg: str):
    def _exception_handler_dec(func):
        async def _wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                await Logger(app).error(msg=msg + " Ошибка: " + str(e), func_name=func_name)

        return _wrapper

    return _exception_handler_dec
