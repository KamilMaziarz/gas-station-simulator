if __name__ == '__main__':
    import random

    import numpy as np

    from gas_station_simulator import SimulationSettings
    from gas_station_simulator import GasStationSimulator

    # pump_working_time - avg time after which ANY of the pumps break
    # e.g. if we have 1 pump and it brakes every 15 days,
    # 2 pumps brake every 7.5 days (7.5*2 -> 2 breaks in 15 days of 2 pumps -> 1 break/pump/15 days),
    # 3 pumps every 5 days (5*3) etc.

    settings = SimulationSettings(
        pumps_quantity=4,
        cashier_quantity=2,
        pump_working_time=lambda: int(np.random.exponential(15 * 24 * 60 * 60 / 4)),
        pump_outage_time=lambda: int(np.random.gamma(6*60*60)),
        customer_fueling_time=lambda: random.randint(2*60, 4*60),
        interaction_with_cashier_time=lambda: random.randint(1*60, 2*60),
        interaction_with_cashier_while_getting_food_time=lambda: random.randint(15, 30),
        food_preparation_time=lambda: random.randint(2*60, 6*60),
        if_eating=lambda: random.random() < 0.6,
        next_car_arrival_time=lambda: random.randint(30, 1*60),
    )
    results = GasStationSimulator(settings=settings).run(time=60*60*24*5)
