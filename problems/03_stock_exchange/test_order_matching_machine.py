from datetime import time
from decimal import Decimal

from order_matching_machine import ORDERTYPE, Order, OrderMatchingMachine, Trade


def make_order(order_id, side, price, quantity):
    # Equal timestamps deliberately exercise submission-order FIFO.
    return Order(order_id, "BAC", Decimal(price), time(9, 45), quantity, side)


def test_original_sample_trades_and_remainders():
    engine = OrderMatchingMachine()
    inputs = [
        ("#1", ORDERTYPE.SELL, "240.12", 100),
        ("#2", ORDERTYPE.SELL, "237.45", 90),
        ("#3", ORDERTYPE.BUY, "238.10", 110),
        ("#4", ORDERTYPE.BUY, "237.80", 10),
        ("#5", ORDERTYPE.BUY, "237.80", 40),
        ("#6", ORDERTYPE.SELL, "236.00", 50),
    ]
    trades = []
    orders = [make_order(*fields) for fields in inputs]
    for order in orders:
        trades.extend(engine.submit_order(order))

    assert trades == [
        Trade("#3", Decimal("237.45"), 90, "#2"),
        Trade("#3", Decimal("236.00"), 20, "#6"),
        Trade("#4", Decimal("236.00"), 10, "#6"),
        Trade("#5", Decimal("236.00"), 20, "#6"),
    ]
    assert [order.remaining_quantity for order in orders] == [100, 0, 0, 0, 20, 0]
    assert [entry[2].id for entry in engine.ask_list] == ["#1"]
    assert [entry[2].id for entry in engine.bid_list] == ["#5"]


def test_best_ask_and_partial_order_retains_fifo_priority():
    engine = OrderMatchingMachine()
    first = make_order("S1", ORDERTYPE.SELL, "100.00", 5)
    cheaper = make_order("S2", ORDERTYPE.SELL, "99.00", 8)
    assert engine.submit_order(first) == []
    assert engine.submit_order(cheaper) == []
    assert engine.submit_order(make_order("B1", ORDERTYPE.BUY, "101.00", 10)) == [
        Trade("B1", Decimal("99.00"), 8, "S2"),
        Trade("B1", Decimal("100.00"), 2, "S1"),
    ]
    later = make_order("S3", ORDERTYPE.SELL, "100.00", 4)
    engine.submit_order(later)
    assert engine.submit_order(make_order("B2", ORDERTYPE.BUY, "100.00", 5)) == [
        Trade("B2", Decimal("100.00"), 3, "S1"),
        Trade("B2", Decimal("100.00"), 2, "S3"),
    ]
    assert first.remaining_quantity == 0
    assert later.remaining_quantity == 2
    assert len(engine.ask_list) == 1 and not engine.bid_list


def test_incoming_sell_uses_best_bid_fifo_and_seller_price():
    engine = OrderMatchingMachine()
    engine.submit_order(make_order("B1", ORDERTYPE.BUY, "101.00", 2))
    engine.submit_order(make_order("B2", ORDERTYPE.BUY, "102.00", 3))
    third = make_order("B3", ORDERTYPE.BUY, "102.00", 3)
    engine.submit_order(third)
    incoming = make_order("S1", ORDERTYPE.SELL, "100.00", 4)
    assert engine.submit_order(incoming) == [
        Trade("B2", Decimal("100.00"), 3, "S1"),
        Trade("B3", Decimal("100.00"), 1, "S1"),
    ]
    assert incoming.remaining_quantity == 0
    assert third.remaining_quantity == 2
    assert engine.bid_list[0][2] is third
    assert not engine.ask_list


def test_noncrossing_prices_then_equality_and_incoming_remainder():
    engine = OrderMatchingMachine()
    ask = make_order("S1", ORDERTYPE.SELL, "100.01", 2)
    bid = make_order("B1", ORDERTYPE.BUY, "100.00", 3)
    assert engine.submit_order(ask) == []
    assert engine.submit_order(bid) == []
    assert ask.remaining_quantity == 2 and bid.remaining_quantity == 3

    incoming = make_order("S2", ORDERTYPE.SELL, "100.00", 5)
    assert engine.submit_order(incoming) == [
        Trade("B1", Decimal("100.00"), 3, "S2"),
    ]
    assert bid.remaining_quantity == 0 and incoming.remaining_quantity == 2
    assert not engine.bid_list
    assert len(engine.ask_list) == 2
    assert engine.ask_list[0][2] is incoming
