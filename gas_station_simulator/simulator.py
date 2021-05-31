if __name__ == '__main__':
    import pprint
    import random

    import numpy as np

    from gas_station_simulator import SimulationSettings, ProfitCalculationSettings, GasStationSimulator, \
        ProfitCalculator

    # pump_working_time - avg time after which ANY of the pumps break
    # e.g. if we have 1 pump and it brakes every 15 days,
    # 2 pumps brake every 7.5 days (7.5*2 -> 2 breaks in 15 days of 2 pumps -> 1 break/pump/15 days),
    # 3 pumps every 5 days (5*3) etc.

    pumps_quantity = 3
    settings = SimulationSettings(
        pumps_quantity=pumps_quantity,
        cashier_quantity=1,
        pump_working_time=lambda: int(np.random.exponential(5 * 24 * 60 * 60 / pumps_quantity)),
        pump_outage_time=lambda: int(np.random.gamma(6*60*60)),
        interaction_with_cashier_time=lambda: random.randint(1*60, 2*60),
        interaction_with_cashier_while_getting_food_time=lambda: random.randint(15, 30),
        food_preparation_time=lambda: random.randint(2*60, 6*60),
        if_eating=lambda: random.random() < 0.6,
        next_car_arrival_time=lambda: random.randint(30, 1*60),
        customer_fuel_needed=lambda: random.randint(30, 70),
        pump_fueling_speed=0.2,
    )
    simulation_time = 60*60*24*4
    gas_station_simulator = GasStationSimulator(settings=settings)
    results = gas_station_simulator.run(time=simulation_time, save=True)

    monitored_resources = gas_station_simulator.get_monitored_resources()

    profit_calculation_settings_ver_1 = ProfitCalculationSettings(
        hot_dog_profit=2.0,
        fuel_profit_per_litre=0.2,
        cashier_hourly_cost=30,
        pump_monthly_depreciation_cost=10_000,
    )

    profit_calculator_ver_1 = ProfitCalculator(
        simulation_settings=settings,
        profit_calculation_settings=profit_calculation_settings_ver_1,
        results=results,
        simulation_time=simulation_time,
    )
    profit_results_ver_1 = profit_calculator_ver_1.calculate()
    pprint.PrettyPrinter(depth=4).pprint(profit_results_ver_1)
