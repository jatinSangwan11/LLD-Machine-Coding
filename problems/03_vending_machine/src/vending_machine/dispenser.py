from __future__ import annotations

from csv import Error
from dataclasses import dataclass
from readline import insert_text
from statistics import quantiles


Cash = dict[int, int]


@dataclass(frozen=True)
class Product:
    name: str
    product_id: str
    price: int

    def __post_init__(self) -> None:
        if self.price <= 0:
            raise ValueError("price should be positive")


class VendingSlot:
    def __init__(
        self,
        product: Product,
        quantity: int,
        capacity: int,
    ) -> None:
        self.product = product
        self.quantity = quantity
        self.capacity = capacity

    def check_item_available(self) -> bool:  # its responsibility is to check whether this slot has this
        # particular product_id or not and if yes then return the quantity if >0
        return self.quantity > 0

    def dispense_item(self) -> Product:         # protect the quantity of the product and return the product
        if self.check_item_available() == False:
            raise ValueError("Quantity less than 1")
        self.quantity -=1

        return self.product


class PurchaseTransaction:
    def __init__(self, selected_slot: VendingSlot) -> None:
        self.selected_slot = selected_slot
        self.inserted_cash: Cash = {}

    def record_cash(self, denomination: int) -> None:
        """
            check whether the denomination exist or not if not build one else update it 
        """

        # if denomination not in self.inserted_cash:
        #     self.inserted_cash[denomination] =1
        # else:
        #     self.inserted_cash[denomination] +=1      The below is the short trick for the same
        self.inserted_cash[denomination] = (
            self.inserted_cash.get(denomination, 0) + 1
        )

    def total_inserted(self) -> int:
        return sum(key * value for key, value in self.inserted_cash.items())

    def remaining_amount(self) -> int:
        return max(self.selected_slot.product.price -  self.total_inserted(), 0)

    def change_required(self) -> int:
        return max(self.total_inserted() - self.selected_slot.product.price, 0)


    def cash_for_refund(self) -> Cash:
        """ returns the copy of the inserted denominations so they can refund safely """
        return dict(self.inserted_cash)


class CashInventory:
    def __init__(self, denomination_counts: Cash | None = None) -> None: # 1,2,5,10,20,50
        self.denomination_counts = dict(denomination_counts or {})

    def find_change(
        self,
        required_amount: int,   # this is the total change that must be returned
        incoming_cash: Cash,) -> Cash | None:   # this is the cash dict that is given by the issue during the purchase of product
        """Return an exact change plan without modifying stored cash."""
        if required_amount < 0:
            raise ValueError("required amount cannot be negative")
        if required_amount == 0:
            return {}

        # Here is we make a temporary copy of the current cash inventory
        available_cash = dict(self.denomination_counts)
        for denomination, count in incoming_cash.items():
            available_cash[denomination] = (
                available_cash.get(denomination, 0) + count
            )

        denominations = sorted(available_cash, reverse=True)    # this only gives me sorted keys
  
        def search(index: int, amount_left: int) -> Cash | None:
            if amount_left == 0:
                return {}
            if index == len(denominations):
                return None

            denomination = denominations[index]
            available_count = available_cash[denomination]
            maximum_usable = min(
                available_count,
                amount_left // denomination,
            )

            for count in range(maximum_usable, -1, -1):
                remaining = amount_left - denomination * count
                smaller_change = search(index + 1, remaining)
                if smaller_change is not None:
                    if count > 0:
                        return {
                            denomination: count,
                            **smaller_change,
                        }
                    return smaller_change

            return None

        return search(0, required_amount)

    def apply_purchase(
        self,
        incoming_cash: Cash,
        returned_change: Cash,
    ) -> None:
        # available_cash = self.denomination_counts # this means the available_cash points to the same dictionary but below is the copy of it
        available_cash = dict(self.denomination_counts)
        for den, count in incoming_cash.items():
            available_cash[den] = (
                available_cash.get(den, 0)+count
            )
        
        for den, count in returned_change.items():
            available_count = available_cash.get(den, 0)
            if count < 0:
                raise ValueError("returned change count cannot be negative")
            if available_count < count:
                raise ValueError(
                    "not enough cash for the returned change"
                )

            available_cash[den] = available_count - count

        self.denomination_counts = available_cash
        

        


class VendingMachine:
    def __init__(
        self,
        slots: dict[str, VendingSlot],
        cash_inventory: CashInventory,
    ) -> None:
        self.slots = slots
        self.cash_inventory = cash_inventory
        self.active_transaction: PurchaseTransaction | None = None
 
    def view_products(self) -> list[dict[str, str | int | bool]]:
        return [
            {
                "product_id": slot.product.product_id,
                "name": slot.product.name,
                "price": slot.product.price,
                "available": slot.check_item_available(),
            }
            for slot in self.slots.values()
        ]

    def select_product(self, product_id: str) -> dict[str, str | int]:
        # checking the availability of the product_id
        if product_id not in self.slots:
            raise ValueError("No slot holds this product")

        available_slot = self.slots[product_id]
        if(available_slot.check_item_available() == False): #Quantity check
            raise ValueError("Not enough Quantity")

        if(self.active_transaction is None):
            self.active_transaction = PurchaseTransaction(available_slot)
        else :
            raise ValueError("There is already a existing transaction")

        product = available_slot.product
        return {
            "product_id": product.product_id,
            "name": product.name,
            "price": product.price,
            "amount_due": product.price,
        }



    def insert_cash(self, denomination: int):
        if self.active_transaction is None:
            raise ValueError("No active transaction")

        transaction = self.active_transaction
        transaction.record_cash(denomination)
        total_cash = transaction.total_inserted()
        remaining_cash = transaction.remaining_amount()

        if remaining_cash > 0:  # if there is still remaining amount then continue with the process
            return total_cash, remaining_cash

        change_needed = transaction.change_required()
        change_plan = self.cash_inventory.find_change(
            change_needed,
            transaction.inserted_cash,
        )
        if change_plan is None:         # Refund plan 
            refunded_cash = transaction.cash_for_refund()
            self.active_transaction = None
            return None, refunded_cash

        # this is the purchase being made
        product = transaction.selected_slot.dispense_item()
        self.cash_inventory.apply_purchase(
            transaction.inserted_cash,
            change_plan,
        )
        self.active_transaction = None

        return product, change_plan

    def cancel_transaction(self):
        # if I cancel as transaction that means it was already active and I need to know if we have got funds in the
        # transaction or not is yes return those refund those and close the trxn
        if self.active_transaction is None:
            raise ValueError("There is no active transaction")
        
        trxn = self.active_transaction
        refund_cash = trxn.cash_for_refund()
        self.active_transaction = None

        return refund_cash
