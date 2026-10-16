from vending_machine.dispenser import (
    CashInventory,
    Product,
    VendingMachine,
    VendingSlot,
)


def test_select_product_returns_payment_details_and_starts_transaction() -> None:
    product = Product(
        name="Coke",
        product_id="P1",
        price=35,
    )
    slot = VendingSlot(
        product=product,
        quantity=2,
        capacity=5,
    )
    machine = VendingMachine(
        slots={"P1": slot},
        cash_inventory=CashInventory(),
    )

    selection = machine.select_product("P1")

    assert selection == {
        "product_id": "P1",
        "name": "Coke",
        "price": 35,
        "amount_due": 35,
    }
    assert machine.active_transaction is not None
    assert machine.active_transaction.selected_slot is slot


def test_customer_buys_product_and_receives_change() -> None:
    product = Product(
        name="Coke",
        product_id="P1",
        price=35,
    )
    slot = VendingSlot(
        product=product,
        quantity=2,
        capacity=5,
    )
    cash_inventory = CashInventory({5: 1})
    machine = VendingMachine(
        slots={"P1": slot},
        cash_inventory=cash_inventory,
    )

    selection = machine.select_product("P1")
    payment_progress = machine.insert_cash(20)
    dispensed_product, returned_change = machine.insert_cash(20)

    assert selection == {
        "product_id": "P1",
        "name": "Coke",
        "price": 35,
        "amount_due": 35,
    }
    assert payment_progress == (20, 15)
    assert dispensed_product is product
    assert returned_change == {5: 1}
    assert slot.quantity == 1
    assert cash_inventory.denomination_counts == {5: 0, 20: 2}
    assert machine.active_transaction is None


def test_purchase_is_refunded_when_exact_change_is_unavailable() -> None:
    product = Product(
        name="Coke",
        product_id="P1",
        price=35,
    )
    slot = VendingSlot(
        product=product,
        quantity=2,
        capacity=5,
    )
    cash_inventory = CashInventory()
    machine = VendingMachine(
        slots={"P1": slot},
        cash_inventory=cash_inventory,
    )

    machine.select_product("P1")
    payment_progress = machine.insert_cash(20)
    dispensed_product, refunded_cash = machine.insert_cash(20)

    assert payment_progress == (20, 15)
    assert dispensed_product is None
    assert refunded_cash == {20: 2}
    assert slot.quantity == 2
    assert cash_inventory.denomination_counts == {}
    assert machine.active_transaction is None


def test_customer_can_cancel_an_active_transaction() -> None:
    product = Product(
        name="Coke",
        product_id="P1",
        price=35,
    )
    slot = VendingSlot(
        product=product,
        quantity=2,
        capacity=5,
    )
    cash_inventory = CashInventory({5: 1})
    machine = VendingMachine(
        slots={"P1": slot},
        cash_inventory=cash_inventory,
    )

    machine.select_product("P1")
    machine.insert_cash(20)
    refunded_cash = machine.cancel_transaction()

    assert refunded_cash == {20: 1}
    assert slot.quantity == 2
    assert cash_inventory.denomination_counts == {5: 1}
    assert machine.active_transaction is None
