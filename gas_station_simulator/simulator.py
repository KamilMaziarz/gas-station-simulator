if __name__ == '__main__':
    import itertools
    import pprint
    import random

    import numpy as np
    import pandas as pd

    from gas_station_simulator import SimulationSettings, ProfitCalculationSettings, GasStationSimulator, \
        ProfitCalculator

    random.seed(0)

    # pump_working_time - avg time after which ANY of the pumps break
    # e.g. if we have 1 pump and it brakes every 15 days,
    # 2 pumps brake every 7.5 days (7.5*2 -> 2 breaks in 15 days of 2 pumps -> 1 break/pump/15 days),
    # 3 pumps every 5 days (5*3) etc.

    simulation_time = 60 * 60 * 24 * 30

    hot_dog_margin = 2.5
    checkout_monthly_cost = 40_000
    fuel_margin_index = -1

    fuel_margin_range = np.arange(0.1, 0.41, 0.1)
    pumps_quantity_range = range(2, 13, 2)
    cashiers_quantity_range = range(1, 5)
    cars_road_flow_range = range(60_000, 100_001, 20_000)
    pumps_cost_range = np.arange(40_000, 100_001, 30_000)

    margin_arrivals_impact_by_fuel_margin = dict(zip(fuel_margin_range, np.linspace(0, -0.2, len(fuel_margin_range))))
    every_n_car_to_enter_the_station = 50

    all_combinations = itertools.product(*[
        fuel_margin_range,
        pumps_quantity_range,
        cashiers_quantity_range,
        cars_road_flow_range,
        pumps_cost_range,
    ])

    all_combinations_results = pd.DataFrame()

    for fuel_margin, pumps_quantity, cashiers_quantity, cars_road_flow, pumps_cost_range in all_combinations:
        cars_per_second_on_the_road = cars_road_flow/(24*60*60)
        cars_per_second_to_enter_the_station = cars_per_second_on_the_road/every_n_car_to_enter_the_station
        average_seconds_per_car_to_enter_the_station = 1/cars_per_second_to_enter_the_station

        margin_arrivals_impact = margin_arrivals_impact_by_fuel_margin[fuel_margin]
        average_arrival_time = average_seconds_per_car_to_enter_the_station/(1+margin_arrivals_impact)

        settings = SimulationSettings(
            pumps_quantity=pumps_quantity,
            cashiers_quantity=cashiers_quantity,
            pump_working_time=lambda: int(np.random.exponential(2 * 24 * 60 * 60 / pumps_quantity)),
            pump_outage_time=lambda: int(np.random.gamma(50 * 60, 250 / (50 * 60))),
            interaction_with_cashier_time=lambda: int(np.random.normal(2 * 60, 20)),
            interaction_with_cashier_while_getting_food_time=lambda: random.randint(30, 60),
            food_preparation_time=lambda: random.randint(2 * 60, 3 * 60),
            if_eating=lambda: np.random.binomial(1, 0.4) == 1,
            next_car_arrival_time=lambda: int(np.random.exponential(average_arrival_time)),
            customer_fuel_needed=lambda: int(np.random.exponential(50)),
            pump_fueling_speed=0.2,
        )

        gas_station_simulator = GasStationSimulator(settings=settings)
        results = gas_station_simulator.run(time=simulation_time, save=False)

        # monitored_resources = gas_station_simulator.get_monitored_resources()

        profit_calculation_settings = ProfitCalculationSettings(
            hot_dog_profit=hot_dog_margin,
            fuel_profit_per_litre=fuel_margin,
            cashier_hourly_cost=checkout_monthly_cost / 30 / 24,
            pump_monthly_depreciation_cost=10_000,
        )

        profit_calculator = ProfitCalculator(
            simulation_settings=settings,
            profit_calculation_settings=profit_calculation_settings,
            results=results,
            simulation_time=simulation_time,
        )
        profit_results = profit_calculator.calculate()
        simulation_combination = {
            'fuel_margin': fuel_margin,
            'pumps_quantity': pumps_quantity,
            'cashiers_quantity': cashiers_quantity,
            'cars_road_flow': cars_road_flow,
            'pumps_cost_range': pumps_cost_range,
        }

        combination_results = pd.DataFrame.from_dict({**profit_results, **simulation_combination}, orient='index').T
        all_combinations_results = pd.concat([all_combinations_results, combination_results])
