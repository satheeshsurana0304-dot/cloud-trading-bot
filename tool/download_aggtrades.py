import asyncio
import json
import websockets


URL = "wss://fstream.binance.com/ws"


async def test_stream():
    print("=" * 55)
    print("BINANCE WEBSOCKET STREAM TEST")
    print("=" * 55)

    async with websockets.connect(
        URL,
        ping_interval=20,
        ping_timeout=20,
    ) as ws:

        print("Connected to Binance WebSocket")

        request = {
            "method": "SUBSCRIBE",
            "params": [
                "btcusdt@aggTrade",
                "1000pepeusdt@aggTrade",
            ],
            "id": 1,
        }

        await ws.send(json.dumps(request))

        print("Subscription request sent.")
        print("Waiting for Binance messages...")
        print("-" * 55)

        while True:
            try:
                message = await asyncio.wait_for(
                    ws.recv(),
                    timeout=15
                )

                data = json.loads(message)

                print("MESSAGE RECEIVED:")
                print(data)
                print("-" * 55)

            except asyncio.TimeoutError:
                print("NO MESSAGE RECEIVED FOR 15 SECONDS")
                print("Connection is still open.")
                print("-" * 55)


if __name__ == "__main__":
    try:
        asyncio.run(test_stream())
    except KeyboardInterrupt:
        print("\nTest stopped.")