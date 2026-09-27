"""
here we are designing the interfaces and for the first step we are starting with - vending machine here

- vending machine--> 
  view products()
  select_product(product_id)
  insert_cash(denomination) - accepts the denomination and return either payment progress or completed purchase result
  cancel_transaction()

Now for the next step we need to define the contract for each public methods:
Input -> succesful result -> possible failure -> state change

ENTITY-1
-view_products()--> input : none, Result- product_code, 
name, price, and availablitiy for every slot(should be boolean for user) --> failure: none --> state change: none

- select_products(product_id) --> input: product_id --> successful result: selected product, price, and amount remaining
-> failure: sold-out product, unknown product, another active transaction 
-> state change: starts a active transaction with zero balance and no inserted cash
- insert_cash --> input: denomination(a particular cash note of a denomination) -> successful result: accepts the payment
and returns the next updated balance with rest of the payment or payment received successfully with any available change to be provided back to the customer
dispensed product --> 
State changes:- Initially, record the denomination in the active transaction.
- On success, decrement stock, update machine cash, and clear the transaction.
- On refund, clear the transaction without changing stock or committed cash.
--> failure: the denomination of the note provided does not match, if paid in full check for any return change
,if the change is not availble with us

cancel_transaction() --> input: active transaction already know the product ---> successful result: cancelled successfully 
and the deposited cash returned
--> failure: no active transaction exits --> state change: remove the active transaction, product stock and committed machin e
cash remain unchanged

Now, what is state - it is any information that is remembered between method calls:
Examples:

- VendingMachine: its active-transaction reference changes.
- PurchaseTransaction: inserted denominations and balance change.
- VendingSlot: quantity changes.
- CashInventory: stored denomination counts change.
- Product: normally no state change because its ID, name, and price remain fixed.

VendingMachine

Data:

- slots
- cash_inventory
- active_transaction

Behavior:

- view_products()
- select_product(product_id)
- insert_cash(denomination)
- cancel_transaction()

ENTITY-2

Product - it represents stable information for a particular product

- product_id
- name
- price

Invariants: product_id cannot be empty, name cannot be empty, price must be greater than zero
@dataclass(frozen=True)
class Product:
    product_id: str
    name: str
    price: int

```
def __post_init__(self) -> None:
    # Validate ID, name, and price.
    ...
```

ENTITy-3 
Vending slot ---- it becomes the clear owner of inventory rules

- product
- capacity
- quantity

behaviour: check whether an item is available, dispense an item( this is the responsibility it has)

ENTITY-4

Purchase Transaction - one customers payment transaction is short lived(temporary memory) and the vending machine is long lived

- as the puchase transaction is a temporary information which is spread across permanent vending machine object

we group all the information about current customer into one object- and we are gonna see what responsibilities it has
and also what data it owns
-- it should remember the customer selected slot 
-- and the inserted cash by the customer

and for the behaviour part-- it should have something like- record_cash(denomination) --> that updates the inserted_cash
-- calculate total inserted ,  calculate the remaining amount , calculate how much change is required, provide cash for refund

PurchaseTransaction

Data:

- selected_slot
- inserted_cash

Behavior:

- record_cash(denomination)
- total_inserted()
- remaining_amount()
- change_required()
- cash_for_refund()

ENTITY-5
CashInventory

Data:

- denomination_counts

Behavior:

- find_change(required_amount, incoming_cash)
- apply_purchase(incoming_cash, returned_change)
"""

