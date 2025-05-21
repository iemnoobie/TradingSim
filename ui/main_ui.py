import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from src.orderbook_handler import OrderBook
import joblib
import numpy as np
import pandas as pd
from models.market_impact import AlmgrenChrissModel
from src.websocket_client import start_websocket_background
import time

# Shared OrderBook instance
if "orderbook" not in st.session_state:
    st.session_state.orderbook = OrderBook(depth_limit=20)
orderbook = st.session_state.orderbook

# Start WebSocket stream 
if "stream_started" not in st.session_state:
    start_websocket_background(st.session_state.orderbook)
    st.session_state.stream_started = True
    st.session_state.orderbook_logs = []

ui_time_start = time.time()
#Left Panel: User Inputs
st.sidebar.title("Trade Simulation Settings")
st.sidebar.markdown("## Input Parameters")

symbol = st.sidebar.selectbox("Spot Asset", ["BTC-USDT-SWAP", "ETH-USDT-SWAP"])
order_type = st.sidebar.selectbox("Order Type", ["Market"])
side = st.sidebar.radio("Trade Side", ["buy", "sell"])
quantity_usd = st.sidebar.number_input("Quantity (USD)", min_value=1, max_value=100000000000, value=100)
volatility = st.sidebar.slider("Volatility (%)", 0.1, 5.0, 1.5)
fee_tier = st.sidebar.selectbox("Fee Tier", ["tier1", "tier2", "tier3"])
fee_map = {
    "tier1": {"maker": 0.0002, "taker": 0.0005},
    "tier2": {"maker": 0.0001, "taker": 0.0004},
    "tier3": {"maker": 0.0, "taker": 0.0003},
}

# Load models
slippage_model = joblib.load("models/slippage_model.pkl")
taker_model = joblib.load("models/taker_model.pkl")
SIGMA = 0.015  
ETA = 0.0005
GAMMA = 0.0001

st.title("OKX Real-Time Trade Simulator")
st.markdown("### Live Output")

# Refreshing every 3 seconds to show updated orderbook
st.experimental_rerun = st.experimental_rerun if hasattr(st, 'experimental_rerun') else lambda: None
st.markdown("### Live Order Book")
col1, col2 = st.columns(2)
with col1:
    st.write("**Bids**")
    st.dataframe(pd.DataFrame(orderbook.bids[:10], columns=["Price","Size(BTC)"]))
with col2:
    st.write("**Asks**")
    st.dataframe(pd.DataFrame(orderbook.asks[:10], columns=["Price","Size(BTC)"]))

# Live Logs Display
st.markdown("### 🧾 Order Book Logs")
latest_log = f"🟢 Bid: {orderbook.get_best_bid():.2f} | Ask: {orderbook.get_best_ask():.2f} | Mid: {orderbook.get_mid_price():.2f} | Spread: {orderbook.get_spread():.2f}"
st.session_state.orderbook_logs.append(latest_log)
st.text_area("Streaming Log", value="\n".join(st.session_state.orderbook_logs[-10:]), height=200)

ui_time_end = time.time()
ui_time = ui_time_end - ui_time_start

# Trade Simulation
if st.button("Simulate Trade"):
    simulation_start = time.time()
    result = orderbook.simulate_market_order(side=side, usd_amount=quantity_usd)
    simulation_end = time.time()

    simulation_time = simulation_end - simulation_start

    if "error" in result:
        st.error(result["error"])
    else:
        spread = orderbook.get_spread()
        order_size = quantity_usd
        quote_distance = spread / result["mid_price"] if result["mid_price"] > 0 else 0.001
        imbalance = 0.5  # 

        # Predict slippage
        slippage_input = pd.DataFrame([[order_size, spread, volatility]],
                              columns=['order_size', 'spread', 'volatility'])
        slippage_pct = slippage_model.predict(slippage_input)[0]

        # Predict taker probability
        taker_input = pd.DataFrame([[spread, imbalance, quote_distance]],
                           columns=['spread', 'imbalance', 'quote_distance'])
        taker_prob = taker_model.predict_proba(taker_input)[0][1]

        # Estimate execution_time from order book (simplified: depth levels / 2)
        execution_time = max(1, len(orderbook.asks if side == "buy" else orderbook.bids) // 2)

        # Market impact
        impact_model = AlmgrenChrissModel(sigma=SIGMA, eta=ETA, gamma=GAMMA)
        impact_result = impact_model.compute_impact(order_size, execution_time)

        fee_pct = fee_map[fee_tier]["taker"]
        fee_usd = quantity_usd * fee_pct
        slippage_usd = (slippage_pct / 100) * quantity_usd
        net_cost = slippage_usd + fee_usd + impact_result["total_impact"]

        st.markdown("### Simulation Results")
        st.markdown(f"- Executed Volume: {result['volume']:.6f} BTC")
        st.markdown(f"- Avg Execution Price: ${result['avg_price']:.2f}")
        st.markdown(f"- Mid Price: ${result['mid_price']:.2f}")
        st.markdown(f"- Slippage: {slippage_pct:.2f}% → ${slippage_usd:.2f}")
        st.markdown(f"- Fee: {fee_pct*100:.2f}% → ${fee_usd:.2f}")
        st.markdown(f"- Market Impact: ${impact_result['total_impact']:.2f} (T: ${impact_result['temporary_impact']:.2f}, P: ${impact_result['permanent_impact']:.2f})")
        st.markdown(f"- Maker/Taker Likelihood (Taker): {taker_prob * 100:.2f}%")
        st.success(f"💰 Net Execution Cost: ${net_cost:.2f}")

        st.markdown("### Performance Metrics")
        st.markdown(f"- Data Processing Latency: {orderbook.processing_time * 1000:.2f} ms")
        st.markdown(f"- UI Update Latency: {ui_time * 1000:.2f} ms")
        st.markdown(f"- End-to-End Simulation Latency: {simulation_time * 1000:.2f} ms")



# Force refreshing every 3s for live updates
st_autorefresh = st.empty()
time.sleep(3)
st_autorefresh.button("Refresh", on_click=st.experimental_rerun)
