"""
Mock lease pricing data.

Base monthly prices (GBP) per vehicle, calculated for a standard
36-month / 10,000 miles per year plan. Pricing logic applies
term and mileage multipliers on top of these base rates.
"""

# Base monthly payment (GBP) per vehicle ID at standard terms (36mo, 10k mi/yr)
VEHICLE_BASE_PRICES: dict[str, float] = {
    "1": 450.0,  # Tesla Model 3 Long Range RWD
    "2": 520.0,  # Tesla Model Y Long Range AWD
    "3": 580.0,  # BMW i4 eDrive40
    "4": 410.0,  # Volkswagen ID.4 Pro Performance
    "5": 390.0,  # Hyundai IONIQ 6
    "6": 490.0,  # Polestar 2 Long Range Single Motor
    "7": 430.0,  # Kia EV6 GT-Line AWD
    "8": 420.0,  # Mercedes-Benz EQA 250+
    "9": 510.0,  # Audi Q4 e-tron 45 quattro
    "10": 400.0,  # Nissan Ariya 87kWh Evolve+
}

# Excess mileage rate (GBP per mile) per vehicle ID
VEHICLE_EXCESS_MILEAGE_RATES: dict[str, float] = {
    "1": 0.12,
    "2": 0.14,
    "3": 0.15,
    "4": 0.11,
    "5": 0.10,
    "6": 0.13,
    "7": 0.11,
    "8": 0.11,
    "9": 0.13,
    "10": 0.10,
}

# Supported lease terms (months)
SUPPORTED_TERMS: list[int] = [24, 36, 48]

# Term multipliers — longer terms are slightly cheaper per month
TERM_MULTIPLIERS: dict[int, float] = {
    24: 1.08,
    36: 1.00,
    48: 0.94,
}

# Annual mileage tiers and their multipliers
MILEAGE_TIERS: list[tuple[int, float]] = [
    (8_000, 0.94),
    (10_000, 1.00),
    (12_000, 1.06),
    (15_000, 1.13),
    (20_000, 1.22),
]

# Initial payment is always 3 months upfront
INITIAL_PAYMENT_MONTHS = 3
