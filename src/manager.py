from src.models import (
    Apartment,
    ApartmentSettlement,
    Bill,
    Parameters,
    Tenant,
    Transfer,
)


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True
    
    def get_apartment_costs(self, apartment_key: str, year: int | None = None, month: int | None = None) -> float | None:
        if apartment_key not in self.apartments:
            return None

        return sum(
            bill.amount_pln
            for bill in self.bills
            if bill.apartment == apartment_key
            and (year is None or bill.settlement_year == year)
            and (month is None or bill.settlement_month == month)
        )

    def get_apartment_transfers(self, apartment_key: str, year: int | None = None, month: int | None = None) -> float | None:
        if apartment_key not in self.apartments:
            return None

        tenant_keys = {
            key for key, tenant in self.tenants.items()
            if tenant.apartment == apartment_key
        }

        return sum(
            transfer.amount_pln
            for transfer in self.transfers
            if transfer.tenant in tenant_keys
            and (year is None or transfer.settlement_year == year)
            and (month is None or transfer.settlement_month == month)
        )

    def get_apartment_settlement(self, apartment_key: str, year: int, month: int) -> ApartmentSettlement | None:
        if apartment_key not in self.apartments:
            return None

        total_bills = self.get_apartment_costs(apartment_key, year, month)
        total_transfers = self.get_apartment_transfers(apartment_key, year, month)
        total_rent = sum(
            tenant.rent_pln for tenant in self.tenants.values()
            if tenant.apartment == apartment_key
        )

        return ApartmentSettlement(
            apartment=apartment_key,
            year=year,
            month=month,
            total_rent_pln=total_rent,
            total_bills_pln=total_bills,
            total_due_pln=total_rent + total_bills,
            balance_pln=total_transfers - total_bills,
        )
