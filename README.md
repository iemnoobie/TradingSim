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


---

## ⚙️ Features

- 🧮 **Market Impact Modeling** — Simulate the cost of large orders using historical impact regressions.
- 📉 **Real-time L2 Orderbook Feed** — Connects to crypto exchange WebSocket (e.g., OKX) for accurate simulations.
- 📦 **Pluggable ML Models** — Includes pre-trained models for slippage and taker behavior.
- 📊 **Logging and Snapshotting** — Logs app behavior and snapshots for offline analysis.

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/TradeSimulator.git
cd TradeSimulator

### 2.Create a Virtual Enviornment
```bash
python -m venv venv
source venv/bin/activate

### 3. Install Dependencies
```bash
pip install -r requirements.txt
