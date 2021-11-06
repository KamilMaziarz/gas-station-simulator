if __name__ == '__main__':
    import random

    import numpy as np

    from gas_station_simulator import SimulationSettings, ProfitCalculationSettings, GasStationSimulator, \
        ProfitCalculator

    random.seed(0)

    simulation_time = 60**2 * 24 * 30

    cars_road_flow = 80_000
    margin_arrivals_impact = -0.1
    every_n_car_to_enter_the_station = 50
    cars_per_second_on_the_road = cars_road_flow/(24*60*60)
    cars_per_second_to_enter_the_station = cars_per_second_on_the_road/every_n_car_to_enter_the_station
    average_seconds_per_car_to_enter_the_station = 1/cars_per_second_to_enter_the_station
    average_arrival_time = average_seconds_per_car_to_enter_the_station/(1+margin_arrivals_impact)

    pumps_quantity = 10
    settings = SimulationSettings(
        pumps_quantity=pumps_quantity,
        cashiers_quantity=3,
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

    monitored_resources = gas_station_simulator.get_monitored_resources()

    checkout_monthly_cost = 40_000
    profit_calculation_settings = ProfitCalculationSettings(
        hot_dog_profit=2.5,
        fuel_profit_per_litre=0.2,
        cashier_hourly_cost=checkout_monthly_cost / 30 / 24,
        pump_monthly_depreciation_cost=50_000,
    )

    profit_calculator = ProfitCalculator(
        simulation_settings=settings,
        profit_calculation_settings=profit_calculation_settings,
        results=results,
        simulation_time=simulation_time,
    )
    profit_results = profit_calculator.calculate()
    print(profit_results)
