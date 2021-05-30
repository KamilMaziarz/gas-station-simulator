import itertools
import random
from typing import List, Generator, Any, Union

import pandas as pd
from simpy import Event

from gas_station_simulator._customer import _Customer, CustomerData
from gas_station_simulator._environment import _SimulationEnvironment
from gas_station_simulator._gas_station import _GasStation
from gas_station_simulator._settings import SimulationSettings


class GasStationSimulator:
    def __init__(self, settings: SimulationSettings):
        self._settings = settings
        self._customers_results: List[CustomerData] = []

    def run(self, time: int, return_dataframe: bool = True) -> Union[List[CustomerData], pd.DataFrame]:
        random.seed(0)
        environment = _SimulationEnvironment()
        gas_station = _GasStation(environment, settings=self._settings)
        environment.process(self._car_generator(environment=environment, gas_station=gas_station))
        environment.run(until=time)
        if return_dataframe:
            results = self._transform_results_to_dataframe(results=self._customers_results)
        else:
            results = self._customers_results
        return results

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
        transformed_results = pd.DataFrame()

        for customer_result in results:
            customer_data = {}
            for key in customer_result.__dict__.keys():
                customer_data[key] = [getattr(customer_result, key)]
            transformed_results = pd.concat([transformed_results, pd.DataFrame(customer_data)])

        return transformed_results
