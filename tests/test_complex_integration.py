import pytest

from src.manager import Manager
from src.models import Parameters


def test_costs_for_missing_apartment():
    parameters = Parameters()
    manager = Manager(parameters)

    with pytest.raises(KeyError):
        manager.get_apartment_costs('apart-nieistniejace', 2025, 1)


def test_costs_for_month_without_bills():
    parameters = Parameters()
    manager = Manager(parameters)

    assert manager.get_apartment_costs('apart-polanka', 2025, 7) == 0.0
    assert manager.get_apartment_costs('apart-polanka', 2024, 1) == 0.0


def test_costs_for_month_with_bills():
    parameters = Parameters()
    manager = Manager(parameters)

    january_bills = [
        bill for bill in manager.bills
        if bill.apartment == 'apart-polanka'
        and bill.settlement_year == 2025
        and bill.settlement_month == 1
    ]
    expected = sum(bill.amount_pln for bill in january_bills)

    assert len(january_bills) > 1
    assert manager.get_apartment_costs('apart-polanka', 2025, 1) == expected
    assert manager.get_apartment_costs('apart-polanka', 2025, 1) == 910.0
