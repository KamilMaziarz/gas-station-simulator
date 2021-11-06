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
        results_by_source = {
            'pumps_cost': self._calculate_pumps_cost(),
            'cashiers_cost': self._calculate_cashiers_cost(),
            'hot_dogs_income': self._calculate_hot_dogs_profit(),
            'fuel_income': self._calculate_fuel_profit(),
            'cars_quantity': int(self.results['enter'].sum()),
            'missed_cars_quantity': int(self.results['enter'].size - self.results['enter'].sum()),
        }

        results_by_source_with_totals = self._add_total_cost_and_income(results_by_source=results_by_source)

        months = self.simulation_time / (60**2 * 24 * 30)
        results = {key: int(value/months) for key, value in results_by_source_with_totals.items()}

        results['income_per_car'] = int(results['total_income'] / results['cars_quantity'])
        results['profit'] = results['total_income'] - results['total_cost']
        results['missed_income'] = results['income_per_car'] * results['missed_cars_quantity']

        return results

    def _add_total_cost_and_income(self, results_by_source: Dict[str, float]) -> Dict[str, float]:  # noqa
        for flow_type in ['cost', 'income']:
            values = [value for key, value in results_by_source.items() if flow_type in key]
            results_by_source['total_' + flow_type] = sum(values)
        return results_by_source

    def _calculate_pumps_cost(self) -> int:
        months = self.simulation_time / (60**2 * 24 * 30)
        monthly_cost = \
            self.simulation_settings.pumps_quantity * self.profit_calculation_settings.pump_monthly_depreciation_cost
        return int(monthly_cost * months)

    def _calculate_cashiers_cost(self) -> int:
        hours = self.simulation_time / 60**2
        hourly_cost = self.simulation_settings.cashiers_quantity * self.profit_calculation_settings.cashier_hourly_cost
        return int(hours * hourly_cost)

    def _calculate_hot_dogs_profit(self) -> int:
        return int(self.profit_calculation_settings.hot_dog_profit * self.results['eating'].sum())

    def _calculate_fuel_profit(self) -> int:
        return int(self.profit_calculation_settings.fuel_profit_per_litre * self.results['fuel_needed'].sum())
