import pytest

from src.manager import Manager
from src.models import ApartmentSettlement
from src.models import Parameters
from src.models import Bill

def test_costs_for_missing_apartment():
    parameters = Parameters()
    manager = Manager(parameters)

    assert manager.get_apartment_costs('apart-nieistniejace', 2025, 1) is None


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

def test_apartment_costs_with_optional_parameters():
    manager = Manager(Parameters())
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=2,
        amount_pln=1250.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-15',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=1150.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-02-02',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=222.0,
        type='electricity'
    ))

    costs = manager.get_apartment_costs('apartment-1', 2024, 1)
    assert costs is None

    costs = manager.get_apartment_costs('apart-polanka', 2024, 3)
    assert costs == 0.0

    costs = manager.get_apartment_costs('apart-polanka', 2024, 1)
    assert costs == 222.0

    costs = manager.get_apartment_costs('apart-polanka', 2025, 1)
    assert costs == 910.0
    
    costs = manager.get_apartment_costs('apart-polanka', 2024)
    assert costs == 1372.0

    costs = manager.get_apartment_costs('apart-polanka')
    assert costs == 3532.0


def test_apartment_settlement_with_bills():
    parameters = Parameters()
    manager = Manager(parameters)

    settlement = manager.get_apartment_settlement('apart-polanka', 2025, 1)

    assert isinstance(settlement, ApartmentSettlement)
    assert settlement.apartment == 'apart-polanka'
    assert settlement.year == 2025
    assert settlement.month == 1
    assert settlement.total_bills_pln == 910.0
    assert settlement.total_bills_pln == manager.get_apartment_costs('apart-polanka', 2025, 1)
    assert settlement.total_rent_pln == 4200.0
    assert settlement.total_due_pln == settlement.total_rent_pln + settlement.total_bills_pln
    assert settlement.balance_pln == 7500.0 - 910.0
    assert settlement.balance_pln == 6590.0


def test_apartment_settlement_without_bills():
    parameters = Parameters()
    manager = Manager(parameters)

    settlement = manager.get_apartment_settlement('apart-polanka', 2025, 7)

    assert isinstance(settlement, ApartmentSettlement)
    assert settlement.apartment == 'apart-polanka'
    assert settlement.year == 2025
    assert settlement.month == 7
    assert settlement.total_bills_pln == 0.0
    assert settlement.balance_pln == 0.0
    assert settlement.total_due_pln == settlement.total_rent_pln


def test_apartment_settlement_balance_follows_bills():
    parameters = Parameters()
    manager = Manager(parameters)

    before = manager.get_apartment_settlement('apart-polanka', 2025, 1)

    manager.bills.append(Bill(
        amount_pln=90.0,
        date_due='2025-02-20',
        apartment='apart-polanka',
        settlement_year=2025,
        settlement_month=1,
        type='water'
    ))
    after = manager.get_apartment_settlement('apart-polanka', 2025, 1)

    assert after.total_bills_pln == before.total_bills_pln + 90.0
    assert after.total_bills_pln == 1000.0
    assert after.balance_pln == before.balance_pln - 90.0
    assert after.balance_pln == 6500.0


def test_apartment_settlement_for_missing_apartment():
    parameters = Parameters()
    manager = Manager(parameters)

    assert manager.get_apartment_settlement('apart-nieistniejace', 2025, 1) is None
