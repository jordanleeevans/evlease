import logging

from database import (
    INITIAL_PAYMENT_MONTHS,
    MILEAGE_TIERS,
    SUPPORTED_TERMS,
    TERM_MULTIPLIERS,
    VEHICLE_BASE_PRICES,
    VEHICLE_EXCESS_MILEAGE_RATES,
)

logger = logging.getLogger(__name__)


class LeasingRepository:
    def _mileage_multiplier(self, annual_mileage: int) -> float:
        """Return the multiplier for the closest mileage tier."""
        closest_tier, closest_multiplier = min(
            MILEAGE_TIERS, key=lambda t: abs(t[0] - annual_mileage)
        )
        logger.debug(
            f"Calculating mileage multiplier for {annual_mileage} miles: "
            f"closest tier is {closest_tier} miles with multiplier {closest_multiplier}"
        )
        return closest_multiplier

    def calculate_quote(
        self, vehicle_id: str, term_months: int, annual_mileage_miles: int
    ) -> dict | None:
        base = VEHICLE_BASE_PRICES.get(vehicle_id)
        if base is None:
            logger.debug(f"Vehicle ID {vehicle_id} not found in base prices")
            return None
        if term_months not in SUPPORTED_TERMS:
            logger.debug(f"Term {term_months} months is not supported")
            return None

        term_mult = TERM_MULTIPLIERS[term_months]
        mileage_mult = self._mileage_multiplier(annual_mileage_miles)
        monthly = round(base * term_mult * mileage_mult, 2)
        initial = round(monthly * INITIAL_PAYMENT_MONTHS, 2)
        DEFAULT_EXCESS_RATE = 0.12
        excess_rate = VEHICLE_EXCESS_MILEAGE_RATES.get(vehicle_id, DEFAULT_EXCESS_RATE)

        quote_id = f"{vehicle_id}-{term_months}-{annual_mileage_miles}"
        logger.debug(
            f"Calculated quote {quote_id}: monthly={monthly}, initial={initial}, "
            f"excess_rate={excess_rate}"
        )
        return {
            "id": quote_id,
            "vehicle_id": vehicle_id,
            "term_months": term_months,
            "annual_mileage_miles": annual_mileage_miles,
            "monthly_payment_gbp": monthly,
            "initial_payment_gbp": initial,
            "excess_mileage_rate_gbp": excess_rate,
        }

    def get_lease_plans(self, vehicle_id: str) -> list[dict]:
        """Return all standard term/mileage combinations for a vehicle."""
        standard_mileages = [8_000, 10_000, 12_000, 15_000]
        plans = []
        for term in SUPPORTED_TERMS:
            logger.debug(
                f"Generating lease plans for vehicle {vehicle_id}, term {term} months"
            )
            for mileage in standard_mileages:
                logger.debug(
                    f"Generating lease plan for vehicle {vehicle_id}, "
                    f"term {term} months, mileage {mileage} miles"
                )
                quote = self.calculate_quote(vehicle_id, term, mileage)
                if quote:
                    plans.append(quote)
        logger.info(f"Generated {len(plans)} lease plans for vehicle {vehicle_id}")
        return plans
