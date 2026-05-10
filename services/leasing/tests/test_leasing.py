from fastapi.testclient import TestClient

from main import app
from repositories import LeasingRepository

# ── Repository unit tests ─────────────────────────────────────────────────────


class TestLeasingRepository:
    def setup_method(self):
        self.repo = LeasingRepository()

    def test_calculate_quote_returns_quote_for_known_vehicle(self):
        quote = self.repo.calculate_quote("1", 36, 10_000)
        assert quote is not None
        assert quote["vehicle_id"] == "1"
        assert quote["term_months"] == 36
        assert quote["annual_mileage_miles"] == 10_000

    def test_calculate_quote_returns_none_for_unknown_vehicle(self):
        assert self.repo.calculate_quote("999", 36, 10_000) is None

    def test_calculate_quote_returns_none_for_unsupported_term(self):
        assert self.repo.calculate_quote("1", 12, 10_000) is None
        assert self.repo.calculate_quote("1", 60, 10_000) is None

    def test_calculate_quote_id_is_deterministic(self):
        q1 = self.repo.calculate_quote("1", 36, 10_000)
        q2 = self.repo.calculate_quote("1", 36, 10_000)
        assert q1["id"] == q2["id"]

    def test_calculate_quote_id_format(self):
        quote = self.repo.calculate_quote("3", 24, 12_000)
        assert quote["id"] == "3-24-12000"

    def test_longer_term_is_cheaper_per_month(self):
        q36 = self.repo.calculate_quote("1", 36, 10_000)
        q48 = self.repo.calculate_quote("1", 48, 10_000)
        assert q48["monthly_payment_gbp"] < q36["monthly_payment_gbp"]

    def test_shorter_term_is_more_expensive_per_month(self):
        q24 = self.repo.calculate_quote("1", 24, 10_000)
        q36 = self.repo.calculate_quote("1", 36, 10_000)
        assert q24["monthly_payment_gbp"] > q36["monthly_payment_gbp"]

    def test_higher_mileage_costs_more(self):
        q_low = self.repo.calculate_quote("1", 36, 8_000)
        q_high = self.repo.calculate_quote("1", 36, 15_000)
        assert q_high["monthly_payment_gbp"] > q_low["monthly_payment_gbp"]

    def test_initial_payment_is_three_months(self):
        quote = self.repo.calculate_quote("1", 36, 10_000)
        expected = round(quote["monthly_payment_gbp"] * 3, 2)
        assert quote["initial_payment_gbp"] == expected

    def test_monthly_payment_rounded_to_two_decimal_places(self):
        for vehicle_id in ["1", "3", "5", "7"]:
            quote = self.repo.calculate_quote(vehicle_id, 36, 10_000)
            assert quote["monthly_payment_gbp"] == round(
                quote["monthly_payment_gbp"], 2
            )

    def test_excess_mileage_rate_present(self):
        quote = self.repo.calculate_quote("1", 36, 10_000)
        assert "excess_mileage_rate_gbp" in quote
        assert quote["excess_mileage_rate_gbp"] > 0

    # --- get_lease_plans ---

    def test_get_lease_plans_returns_list(self):
        plans = self.repo.get_lease_plans("1")
        assert isinstance(plans, list)
        assert len(plans) > 0

    def test_get_lease_plans_returns_empty_for_unknown_vehicle(self):
        plans = self.repo.get_lease_plans("999")
        assert plans == []

    def test_get_lease_plans_covers_all_term_and_mileage_combos(self):
        # 3 terms × 4 mileage tiers = 12 plans per vehicle
        plans = self.repo.get_lease_plans("2")
        assert len(plans) == 12

    def test_get_lease_plans_all_have_unique_ids(self):
        plans = self.repo.get_lease_plans("1")
        ids = [p["id"] for p in plans]
        assert len(ids) == len(set(ids))


class TestLeaseQuoteResolver:
    def setup_method(self):
        self.client = TestClient(app)

    def _gql(self, query: str) -> dict:
        response = self.client.post("/graphql/", json={"query": query})
        assert response.status_code == 200
        return response.json()

    def test_lease_quote_returns_data(self):
        result = self._gql("""
            query {
              leaseQuote(vehicleId: "1", termMonths: 36, annualMileageMiles: 10000) {
                id
                termMonths
                annualMileageMiles
                monthlyPaymentGbp
                initialPaymentGbp
                excessMileageRateGbp
              }
            }
        """)
        assert result.get("errors") is None
        quote = result["data"]["leaseQuote"]
        assert quote["id"] == "1-36-10000"
        assert quote["termMonths"] == 36
        assert quote["annualMileageMiles"] == 10_000
        assert quote["monthlyPaymentGbp"] == 450.0
        assert quote["initialPaymentGbp"] == 1350.0

    def test_lease_quote_returns_null_for_unknown_vehicle(self):
        result = self._gql("""
            query {
              leaseQuote(vehicleId: "999", termMonths: 36, annualMileageMiles: 10000) {
                id
              }
            }
        """)
        assert result.get("errors") is None
        assert result["data"]["leaseQuote"] is None

    def test_lease_quote_returns_null_for_invalid_term(self):
        result = self._gql("""
            query {
              leaseQuote(vehicleId: "1", termMonths: 12, annualMileageMiles: 10000) {
                id
              }
            }
        """)
        assert result.get("errors") is None
        assert result["data"]["leaseQuote"] is None

    def test_lease_quote_vehicle_stub_returned(self):
        # In isolation (without the gateway), vehicle resolves to just {id}
        result = self._gql("""
            query {
              leaseQuote(vehicleId: "1", termMonths: 36, annualMileageMiles: 10000) {
                vehicle { id }
              }
            }
        """)
        assert result.get("errors") is None
        assert result["data"]["leaseQuote"]["vehicle"]["id"] == "1"

    def test_lease_plans_returns_all_plans(self):
        result = self._gql("""
            query {
              leasePlans(vehicleId: "1") {
                id
                termMonths
                annualMileageMiles
                monthlyPaymentGbp
              }
            }
        """)
        assert result.get("errors") is None
        plans = result["data"]["leasePlans"]
        assert len(plans) == 12

    def test_lease_plans_returns_empty_for_unknown_vehicle(self):
        result = self._gql("""
            query {
              leasePlans(vehicleId: "999") {
                id
              }
            }
        """)
        assert result.get("errors") is None
        assert result["data"]["leasePlans"] == []

    def test_federation_sdl_exposed(self):
        result = self._gql("{ _service { sdl } }")
        assert result.get("errors") is None
        sdl = result["data"]["_service"]["sdl"]
        assert "LeaseQuote" in sdl
        assert "Vehicle" in sdl
