from dataclasses import dataclass


@dataclass
class Account:
    subject_id: str
    email: str
    enabled: bool


def can_authenticate(account: Account) -> bool:
    return account.enabled
