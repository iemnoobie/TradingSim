import sys
import time
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio
import websockets
import json
import threading
from src.utils import setup_logger
from src.orderbook_handler import OrderBook
print("✅ Successfully imported OrderBook")
import csv

HISTORICAL_FILE = "data/l2_snapshots.csv"

def save_tick_snapshot(timestamp, bids, asks):
    print("📌 save_tick_snapshot called")
    print("   Timestamp:", timestamp)
    print("   Best bid/ask raw:", bids[:1], asks[:1])
    print("   CSV path:", HISTORICAL_FILE)
    print("   CWD:", os.getcwd())
    if not os.path.exists(HISTORICAL_FILE):
        with open(HISTORICAL_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "best_bid", "best_ask", "spread", "mid_price", "top_bid_qty", "top_ask_qty"])

    best_bid = float(bids[0][0]) if bids else 0.0
    best_ask = float(asks[0][0]) if asks else 0.0
    spread = best_ask - best_bid
    mid_price = (best_ask + best_bid) / 2 if best_bid and best_ask else 0.0
    top_bid_qty = float(bids[0][1]) if bids else 0.0
    top_ask_qty = float(asks[0][1]) if asks else 0.0

    try:
        with open(HISTORICAL_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, best_bid, best_ask, spread, mid_price, top_bid_qty, top_ask_qty])
    except Exception as e:
        print("Error writing to CSV")

logger = setup_logger("WebSocketClient")
URL = "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP"
'''
orderbook = OrderBook()

async def stream_orderbook():
    while True:
        try:
            async with websockets.connect(URL, ping_interval=20, ping_timeout=10) as ws:
                logger.info("Connected to OKX WebSocket.")
                print("Got websocket message")
                while True:
                    message = await ws.recv()
                    #print("RAW Message:", message)
                    data = json.loads(message)

                    bids = data.get("bids", [])
                    asks = data.get("asks", [])
                    timestamp = data.get("timestamp", "")

                    # Save this tick for training
                    save_tick_snapshot(timestamp, bids, asks)

                    # Update order book
                    orderbook.update(bids, asks)

                    # Log or print order book stats
                    bid = orderbook.get_best_bid()
                    ask = orderbook.get_best_ask()
                    mid = orderbook.get_mid_price()
                    spread = orderbook.get_spread()
                    depth = orderbook.get_depth(side="buy", usd_amount=100)

                    print(f"🟢 Bid: {bid:.2f} | Ask: {ask:.2f} | Mid: {mid:.2f} | Spread: {spread:.2f}")
                    print(f"📊 Est. base volume to buy $100: {depth:.4f} units")

                    #bid = orderbook.get_best_bid()
                    #ask = orderbook.get_best_ask()
                    #mid = orderbook.get_mid_price()
                    #logger.info(f"{timestamp} | Bid: {bid:.2f}, Ask: {ask:.2f}, Mid: {mid:.2f}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")

if __name__ == "__main__":
    asyncio.run(stream_orderbook())
'''

def start_websocket_background(orderbook: OrderBook):
    async def stream():
        try:
            async with websockets.connect(URL) as ws:
                logger.info("Connected to OKX WebSocket")
                while True:
                    receiving_time = time.time()
                    message = await ws.recv()
                    data = json.loads(message)

                    process_start = time.time()
                    bids = data.get("bids", [])
                    asks = data.get("asks", [])
                    timestamp = data.get("timestamp", "")
                    orderbook.update(bids, asks)
                    process_end = time.time()

                    orderbook.last_tick_time = receiving_time
                    orderbook.processing_time = process_end - process_start

                    bid = orderbook.get_best_bid()
                    ask = orderbook.get_best_ask()
                    mid = orderbook.get_mid_price()
                    spread = orderbook.get_spread()
                    logger.info(f"{timestamp} | Bid: {bid:.2f}, Ask: {ask:.2f}, Mid: {mid:.2f}, Spread: {spread:.2f}")
                    print("✅ WebSocket updated order book:", len(orderbook.bids), len(orderbook.asks))

        except Exception as e:
            logger.error(f"WebSocket error: {e}")

    # Start asyncio loop in new thread
    def runner():
        asyncio.new_event_loop().run_until_complete(stream())

    t = threading.Thread(target=runner, daemon=True)
    t.start()
