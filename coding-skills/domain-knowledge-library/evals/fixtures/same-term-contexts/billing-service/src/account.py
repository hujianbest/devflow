from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Account:
    billing_account_id: str
    outstanding_balance: Decimal
    currency: str


def can_charge(account: Account, amount: Decimal) -> bool:
    return account.outstanding_balance + amount >= Decimal("0")
