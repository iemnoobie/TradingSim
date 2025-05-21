# 🧠 TradeSimulator

A high-performance cryptocurrency trade simulator that leverages real-time Level 2 (L2) orderbook data to estimate transaction costs and market impact. Designed to support research and strategy development using realistic slippage and execution models.

---

## 📁 Project Structure

TRADESIMULATOR/
├── config/ # Configuration files

├── data/ # Raw or snapshot data (excluded from Git)

├── logs/ # Logging output (excluded from Git)
├── models/ # Serialized ML models (e.g., slippage, taker models)
├── src/ # Core source code
│ ├── orderbook_handler.py
│ ├── simulator.py
│ ├── utils.py
│ └── websocket_client.py
├── ui/ # Placeholder for UI integration
├── .env # Environment variables (excluded from Git)
├── main.py # Entry point
├── requirements.txt # Python dependencies
├── config.yaml # Simulation config
└── README.md
