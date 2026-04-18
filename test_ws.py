import asyncio
import websockets

async def listen():
    async with websockets.connect("ws://localhost:8000/ws/devices") as ws:
        print("연결됨. 메시지 대기중...")
        async for msg in ws:
            print("수신:", msg)

asyncio.run(listen())
