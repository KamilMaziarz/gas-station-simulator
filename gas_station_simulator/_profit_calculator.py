from typing import Dict

import pandas as pd

from gas_station_simulator import ProfitCalculationSettings, SimulationSettings


class ProfitCalculator:
    def __init__(
            self,
            simulation_settings: SimulationSettings,
            profit_calculation_settings: ProfitCalculationSettings,
            results: pd.DataFrame,
            simulation_time: int,
    ):
        self.simulation_settings = simulation_settings
        self.profit_calculation_settings = profit_calculation_settings
        self.results = results
        self.simulation_time = simulation_time

    def calculate(self) -> Dict[str, int]:
        return {
            'average_monthly_profit': self.calculate_average_monthly_profit(),
            'average_profit_per_car': self.calculate_average_profit_per_car(),
            'average_missed_monthly_profit': self.calculate_average_missed_monthly_profit(),
        }

    def calculate_average_missed_monthly_profit(self) -> int:
        average_profit_per_car = self.calculate_average_profit_per_car()
        cars_missed = self.results['enter'].size - self.results['enter'].sum()
        missed_profit = cars_missed * average_profit_per_car
        months = self.simulation_time / (60*60*24*30)
        return int(missed_profit / months)

    def calculate_average_profit_per_car(self) -> int:
        total_profit = self.calculate_average_monthly_profit()
        return int(total_profit / self.results['enter'].sum())

    def calculate_average_monthly_profit(self) -> int:
        pumps_cost = self._calculate_pumps_cost()
        cashiers_cost = self._calculate_cashiers_cost()
        hot_dogs_profit = self._calculate_hot_dogs_profit()
        fuel_profit = self._calculate_fuel_profit()
        profit = fuel_profit + hot_dogs_profit - pumps_cost - cashiers_cost
        profit -= self.profit_calculation_settings.other_monthly_costs
        months = self.simulation_time / (60*60*24*30)
        return int(profit / months)

    def _calculate_pumps_cost(self) -> float:
        months = self.simulation_time / (60 * 60 * 24 * 30)
        monthly_cost = \
            self.simulation_settings.pumps_quantity * self.profit_calculation_settings.pump_monthly_depreciation_cost
        total_pumps_cost = monthly_cost * months
        return total_pumps_cost

    def _calculate_cashiers_cost(self) -> float:
        hours = self.simulation_time / (60 * 60)
        hourly_cost = self.simulation_settings.cashier_quantity * self.profit_calculation_settings.cashier_hourly_cost
        total_cashiers_cost = hours * hourly_cost
        return total_cashiers_cost

    def _calculate_hot_dogs_profit(self) -> float:
        return self.profit_calculation_settings.hot_dog_profit * self.results['eating'].sum()

    def _calculate_fuel_profit(self) -> float:
        return self.profit_calculation_settings.fuel_profit_per_litre * self.results['fuel_needed'].sum()
