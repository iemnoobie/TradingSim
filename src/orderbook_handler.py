from typing import List, Tuple


class OrderBook:
    def __init__(self, depth_limit: int = 20):
        """
        Initialize with empty order book. 
        """
        self.depth_limit = depth_limit
        self.bids: List[Tuple[float, float]] = []  # List of (price, size)
        self.asks: List[Tuple[float, float]] = []
        self.last_tick_time = 0
        self.processing_time = 0

    def update(self, bids: List[List[str]], asks: List[List[str]]):
        """
        Update the order book with new L2 data from WebSocket.
        Assumes full refresh (not incremental delta).
        """
        # Clean and convert incoming levels to float
        cleaned_bids = [(float(p), float(s)) for p, s in bids if float(s) > 0]
        cleaned_asks = [(float(p), float(s)) for p, s in asks if float(s) > 0]

        # Sort and truncate to depth_limit
        self.bids = sorted(cleaned_bids, key=lambda x: x[0], reverse=True)[:self.depth_limit]
        self.asks = sorted(cleaned_asks, key=lambda x: x[0])[:self.depth_limit]

    def get_best_bid(self) -> float:
        """Return the best bid price."""
        return self.bids[0][0] if self.bids else 0.0

    def get_best_ask(self) -> float:
        """Return the best ask price."""
        return self.asks[0][0] if self.asks else 0.0

    def get_mid_price(self) -> float:
        """Return the average of best bid and best ask."""
        if self.bids and self.asks:
            return (self.get_best_bid() + self.get_best_ask()) / 2
        return 0.0

    def get_spread(self) -> float:
        """Return the absolute spread in price."""
        if self.bids and self.asks:
            return self.get_best_ask() - self.get_best_bid()
        return 0.0

    def get_depth(self, side: str, usd_amount: float) -> float:
        """
        Estimate how much volume (in base asset) would be consumed 
        to fill a given USD amount on the specified side.
        """
        depth = 0.0
        total_value = 0.0
        levels = self.asks if side == "buy" else self.bids

        for price, size in levels:
            value = price * size
            if total_value + value >= usd_amount:
                # Partial fill at this level
                remaining = usd_amount - total_value
                depth += remaining / price
                break
            else:
                depth += size
                total_value += value

        return depth
    def simulate_market_order(self, side: str, usd_amount: float) -> dict:
            """
            Simulate a market buy/sell order for `usd_amount` USD.
            Returns execution price, volume, slippage, etc.
            """
            levels = self.asks if side == "buy" else self.bids
            if not levels:
                return {"error": "Order book is empty"}

            total_value = 0.0
            total_volume = 0.0
            weighted_sum = 0.0
            remaining = usd_amount

            for price, size in levels:
                value = price * size
                if value >= remaining:
                    partial_volume = remaining / price
                    total_volume += partial_volume
                    weighted_sum += price * partial_volume
                    total_value += remaining
                    break
                else:
                    total_volume += size
                    weighted_sum += price * size
                    total_value += value
                    remaining -= value

            if total_volume == 0:
                return {"error": "Unable to fill order"}

            avg_price = weighted_sum / total_volume
            mid_price = self.get_mid_price()
            slippage = ((avg_price - mid_price) / mid_price) * 100 if mid_price else 0

            return {
                "side": side,
                "usd": usd_amount,
                "volume": total_volume,
                "avg_price": avg_price,
                "mid_price": mid_price,
                "slippage_pct": slippage
            }
