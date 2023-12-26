from traceback import print_exc


def exception_handler(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except:
            print_exc()
    return wrapper
