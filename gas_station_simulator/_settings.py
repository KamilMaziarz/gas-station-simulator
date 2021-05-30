from dataclasses import dataclass
from typing import Callable


@dataclass
class SimulationSettings:
    pumps_quantity: int
    cashier_quantity: int
    pump_working_time: Callable[[], int]
    pump_outage_time: Callable[[], int]
    customer_fuel_needed: Callable[[], int]
    pump_fueling_speed: float
    interaction_with_cashier_time: Callable[[], int]
    interaction_with_cashier_while_getting_food_time: Callable[[], int]
    food_preparation_time: Callable[[], int]
    if_eating: Callable[[], bool]
    next_car_arrival_time: Callable[[], int]


@dataclass
class ProfitCalculationSettings:
    pump_monthly_depreciation_cost: int
    cashier_hourly_cost: float
    hot_dog_profit: float
    fuel_profit_per_litre: float
    other_monthly_costs: int
