import heapq
from dataclasses import dataclass
from datetime import time
from decimal import Decimal
from enum import Enum


class ORDERTYPE(Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class Order:
    id: str
    stock: str
    price: Decimal
    order_time: time
    remaining_quantity: int
    order_type: ORDERTYPE


@dataclass(frozen=True)
class Trade:
    buy_order_id: str
    sell_price: Decimal
    quantity: int
    sell_order_id: str


class OrderMatchingMachine:
    """Single-stock, sequential limit-order matcher.

    Inputs are valid orders with unique IDs for the same stock. Submission
    transfers ownership: do not resubmit or externally mutate a pending order.
    """

    def __init__(self) -> None:
        self.ask_list: list[tuple[Decimal, int, Order]] = []
        self.bid_list: list[tuple[Decimal, int, Order]] = []
        self.arrival_sequence = 0

    def submit_order(self, order: Order) -> list[Trade]:
        # Assign priority on arrival, even if this order will be partly filled.
        # The unique sequence also prevents heapq from comparing Order objects.
        sequence = self.arrival_sequence
        self.arrival_sequence += 1
        trades: list[Trade] = []
        is_buy = order.order_type == ORDERTYPE.BUY
        opposite_heap = self.ask_list if is_buy else self.bid_list

        while order.remaining_quantity > 0 and opposite_heap:
            # Peek without removing: a partially filled resting order stays put.
            resting = opposite_heap[0][2]
            buy = order if is_buy else resting
            sell = resting if is_buy else order

            # If the best opposite price cannot match, no worse price can match.
            # Use actual prices here; negative bid prices are only heap keys.
            if buy.price < sell.price:
                break

            quantity = min(order.remaining_quantity, resting.remaining_quantity)
            trades.append(Trade(buy.id, sell.price, quantity, sell.id))
            order.remaining_quantity -= quantity
            resting.remaining_quantity -= quantity

            if resting.remaining_quantity == 0:
                heapq.heappop(opposite_heap)
            # Otherwise only quantity changed, so price/time heap order is valid.

        if order.remaining_quantity > 0:
            own_heap = self.bid_list if is_buy else self.ask_list
            # A min-heap uses negative bid prices to prioritize the highest bid.
            priority_price = -order.price if is_buy else order.price
            heapq.heappush(own_heap, (priority_price, sequence, order))

        return trades


# Coding takeaway: execute min(buy_remaining, sell_remaining) shares.
# For positive starting quantities, subtracting that amount from both orders
# keeps both remainders nonnegative and makes at least one zero. Every match
# therefore makes progress. min() is not input validation: callers must still
# supply positive quantities under this implementation's valid-input contract.
