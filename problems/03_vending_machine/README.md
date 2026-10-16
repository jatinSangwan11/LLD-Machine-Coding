# Problem 03: Vending Machine

Status: Requirements clarified; successful purchase flow next

## Interview Brief

Design and implement the core software for a vending machine.

At a minimum, a customer should be able to view products, select a product,
pay for it, and receive the product. The machine must also handle inventory and
money correctly when a purchase cannot be completed.

Use Python and keep the first version in memory. No user interface, hardware
integration, network API, database, or distributed coordination is required.

## Clarified Scope

- The machine sells generic packaged products identified by a product code,
  name, and price.
- Each slot holds one product type and has a configured capacity. Initial stock
  and capacity are supplied when the machine is configured.
- One transaction purchases exactly one item. Buying multiple items requires
  multiple transactions.
- The first version accepts cash only, inserted one denomination at a time.
- Supported denominations are ₹1, ₹2, ₹5, ₹10, ₹20, and ₹50.
- A customer selects an in-stock product before inserting money. The machine
  reports the inserted balance and remaining amount after each insertion.
- When the balance reaches or exceeds the price, the machine completes the
  purchase only if it can return the exact change.
- The machine has a finite cash reserve. Inserted cash may be used when
  calculating change for a successful purchase.
- If exact change cannot be returned, the purchase is rejected, all inserted
  denominations are returned, and product stock is unchanged.
- A customer may cancel before a successful vend and receives the exact
  denominations they inserted.
- Invalid selections, sold-out products, and unsupported denominations are
  explicitly rejected without corrupting transaction state.
- On success, exactly one product is dispensed, its stock is decremented, the
  payment is retained, and any required change is returned.
- Only one customer transaction is active at a time; concurrency is out of
  scope for the first version.
- Physical dispenser failures, cards, QR payments, payment gateways, and
  hardware integration are out of scope.

The machine may expose operator operations for restocking products up to slot
capacity and replenishing change, but customer purchasing is the first slice.

## Next Interview Step

Narrate one successful purchase from product selection through dispensing and
change return. Identify the inputs, decisions, state changes, and output at each
step before proposing classes.
