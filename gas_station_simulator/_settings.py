from dataclasses import dataclass
from typing import Callable


@dataclass
class SimulationSettings:
    pumps_quantity: int
    cashier_quantity: int
    pump_working_time: Callable[[], int]
    pump_outage_time: Callable[[], int]
    customer_fueling_time: Callable[[], int]
    interaction_with_cashier_time: Callable[[], int]
    interaction_with_cashier_while_getting_food_time: Callable[[], int]
    food_preparation_time: Callable[[], int]
    if_eating: Callable[[], bool]
    next_car_arrival_time: Callable[[], int]
