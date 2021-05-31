import itertools
import os
from typing import List, Generator, Any, Union

import pandas as pd
from simpy import Event

from gas_station_simulator._customer import _Customer, CustomerData
from gas_station_simulator._environment import _SimulationEnvironment
from gas_station_simulator._gas_station import _GasStation
from gas_station_simulator._monitored_resources import _MONITORED_RESOURCES_PATH
from gas_station_simulator._settings import SimulationSettings


class GasStationSimulator:
    def __init__(self, settings: SimulationSettings):
        self._settings = settings
        self._customers_results: List[CustomerData] = []

    def run(
            self,
            time: int,
            return_dataframe: bool = True,
            save: bool = False,
    ) -> Union[List[CustomerData], pd.DataFrame]:
        environment = _SimulationEnvironment()
        gas_station = _GasStation(environment, settings=self._settings)
        environment.process(self._car_generator(environment=environment, gas_station=gas_station))
        environment.run(until=time)
        if return_dataframe:
            results = self._transform_results_to_dataframe(results=self._customers_results)
        else:
            results = self._customers_results
        if save:
            results.to_csv('results.csv', index=False)
        environment.logger.handlers.clear()
        return results

    def get_monitored_resources(self) -> pd.DataFrame:  # noqa
        monitored_data = pd.DataFrame()
        for file_name in os.listdir(_MONITORED_RESOURCES_PATH):
            if monitored_data.empty:
                monitored_data = pd.read_csv(_MONITORED_RESOURCES_PATH / file_name)
            else:
                monitored_data = pd.merge(
                    monitored_data,
                    pd.read_csv(_MONITORED_RESOURCES_PATH / file_name),
                    on='time',
                    how='outer',
                )
        monitored_data.sort_values(by='time', inplace=True)
        monitored_data = monitored_data.fillna(method='ffill').fillna(method='bfill').reset_index(drop=True)
        return monitored_data

    def _car_generator(
            self,
            environment: _SimulationEnvironment,
            gas_station: _GasStation,
    ) -> Generator[Event, Any, Any]:
        for i in itertools.count():
            yield environment.timeout(self._settings.next_car_arrival_time())
            available_parking_places = gas_station.parking_places.level
            if available_parking_places > 0:
                environment.logger.info('A car is arriving to the station.')
                gas_station.parking_places.get(1)
                customer = _Customer(environment=environment, number=i, settings=self._settings)
                environment.process(self._car_process(environment, gas_station, customer))
            else:
                self._customers_results.append(CustomerData(number=i, enter=False))
                environment.logger.info('A car missed station since there are no left parking places.')

    def _car_process(
            self,
            environment: _SimulationEnvironment,
            gas_station: _GasStation,
            customer: _Customer,
    ) -> Generator[Event, Any, Any]:
        customer_result = yield environment.process(customer.enter(gas_station=gas_station))
        self._customers_results.append(customer_result)

    def _transform_results_to_dataframe(self, results: List[CustomerData]) -> pd.DataFrame:  # noqa
        transformed_results = pd.concat([pd.DataFrame.from_dict(r.__dict__, orient='index').T for r in results])
        transformed_results.sort_values(by='number', inplace=True)
        return transformed_results.reset_index(drop=True)
