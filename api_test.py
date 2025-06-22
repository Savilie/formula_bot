import aiohttp
import asyncio

async def test_connection():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.telegram.org") as resp:
                print(f"Status: {resp.status}")
                return resp.status == 200
    except Exception as e:
        print(f"Connection error: {e}")
        return False

if asyncio.run(test_connection()):
    print("Подключение к Telegram API работает")
else:
    print("Нет подключения к Telegram API")
