import itertools
import random

from gas_station_simulator._settings import SimulationSettings
from gas_station_simulator._customer import _Customer
from gas_station_simulator._environment import _SimulationEnvironment
from gas_station_simulator._gas_station import _GasStation


class GasStationSimulator:
    def __init__(self, settings: SimulationSettings):
        self._settings = settings

    def run(self, time: int):
        random.seed(0)
        environment = _SimulationEnvironment()
        gas_station = _GasStation(environment, settings=self._settings)
        environment.process(self._car_generator(environment=environment, gas_station=gas_station))
        environment.run(until=time)

    def _car_generator(self, environment: _SimulationEnvironment, gas_station: _GasStation):
        for i in itertools.count():
            yield environment.timeout(self._settings.next_car_arrival_time())
            available_parking_places = gas_station.parking_places.level
            if available_parking_places > 0:
                environment.logger.info('A car is arriving to the station.')
                gas_station.parking_places.get(1)
                customer = _Customer(environment=environment, number=i, settings=self._settings)
                environment.process(customer.enter(gas_station=gas_station))
            else:
                environment.logger.info('A car missed station since there are no left parking places.')
