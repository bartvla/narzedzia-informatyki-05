import pytest

from src.manager import Manager
from src.models import ApartmentSettlement
from src.models import Parameters
from src.models import Bill
from src.models import TenantSettlement

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


def test_apartment_costs_with_invalid_month():
    parameters = Parameters()
    manager = Manager(parameters)

    with pytest.raises(ValueError):
        manager.get_apartment_costs('apart-polanka', 2025, 13)

    with pytest.raises(ValueError):
        manager.get_apartment_costs('apart-polanka', 2025, 0)

    assert manager.get_apartment_costs('apart-polanka', 2025, 1) == 910.0


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


def test_tenant_settlements_for_many_tenants():
    parameters = Parameters()
    manager = Manager(parameters)

    apartment_settlement = manager.get_apartment_settlement('apart-polanka', 2025, 1)
    settlements = manager.get_tenant_settlements(apartment_settlement)
    by_tenant = {settlement.tenant: settlement for settlement in settlements}

    expected_share = 910.0 / 3

    assert len(settlements) == 3
    assert all(isinstance(settlement, TenantSettlement) for settlement in settlements)
    assert set(by_tenant) == {'tenant-1', 'tenant-2', 'tenant-3'}
    assert all(settlement.year == 2025 for settlement in settlements)
    assert all(settlement.month == 1 for settlement in settlements)
    assert all(settlement.bills_pln == pytest.approx(expected_share) for settlement in settlements)
    assert sum(settlement.bills_pln for settlement in settlements) == pytest.approx(910.0)
    assert all(settlement.apartment_settlement == 'apart-polanka' for settlement in settlements)
    assert by_tenant['tenant-1'].rent_pln == 1500.0
    assert by_tenant['tenant-3'].rent_pln == 1300.0
    assert by_tenant['tenant-1'].total_due_pln == pytest.approx(1500.0 + expected_share)


def test_tenant_settlements_for_single_tenant():
    parameters = Parameters()
    manager = Manager(parameters)

    del manager.tenants['tenant-2']
    del manager.tenants['tenant-3']

    apartment_settlement = manager.get_apartment_settlement('apart-polanka', 2025, 1)
    settlements = manager.get_tenant_settlements(apartment_settlement)

    assert len(settlements) == 1
    assert settlements[0].tenant == 'tenant-1'
    assert settlements[0].bills_pln == 910.0
    assert settlements[0].bills_pln == apartment_settlement.total_bills_pln
    assert settlements[0].rent_pln == 1500.0
    assert settlements[0].total_due_pln == 2410.0


def test_tenant_settlements_without_tenants():
    parameters = Parameters()
    manager = Manager(parameters)

    manager.tenants.clear()

    apartment_settlement = manager.get_apartment_settlement('apart-polanka', 2025, 1)
    settlements = manager.get_tenant_settlements(apartment_settlement)

    assert settlements == []
    assert len(settlements) == 0
    assert apartment_settlement.total_bills_pln == 910.0
