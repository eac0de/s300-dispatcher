import asyncio


from database import init_db


async def func():
    pass


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(init_db())
        loop.run_until_complete(func())
    finally:
        loop.close()
