import copy
from dataclasses import dataclass, field
from typing import Optional, Generator, Any

import simpy
from simpy import Event

from gas_station_simulator._environment import _SimulationEnvironment
from gas_station_simulator._gas_station import _GasStation
from gas_station_simulator._settings import SimulationSettings


@dataclass
class CustomerData:
    number: int
    enter: bool
    name: str = field(init=False, repr=False)
    fuel_needed: int = field(init=False, repr=False)
    expected_fueling_time: int = field(init=False, repr=False)
    eating: bool = field(init=False, repr=False)
    arrival_time: int = field(init=False, repr=False)
    fueling_start_time: int = field(init=False, repr=False)
    fueling_end_time: int = field(init=False, repr=False)
    interacting_with_cashier_start_time: int = field(init=False, repr=False)
    interacting_with_cashier_end_time: int = field(init=False, repr=False)
    waiting_for_food_time_start_time: Optional[int] = field(init=False, repr=False)
    waiting_for_food_time_end_time: Optional[int] = field(init=False, repr=False)


class _Customer:
    def __init__(self, environment: _SimulationEnvironment, number: int, settings: SimulationSettings):
        self.env = environment
        self._settings = settings

        self.data = CustomerData(number=number, enter=True)
        self.data.name = f'Car {number}'

        fuel_needed = self._settings.customer_fuel_needed()
        self.data.fuel_needed = fuel_needed
        self.data.expected_fueling_time = int(fuel_needed / self._settings.pump_fueling_speed)
        self.data.eating = self._settings.if_eating()

        self._fuel_gotten = 0

    def enter(self, gas_station: _GasStation) -> Generator[Event, Any, Any]:
        self.data.arrival_time = self.env.now
        self.env.logger.info(f'[{self.data.name}]: Entering the station.')

        left_fueling_time = copy.copy(self.data.expected_fueling_time)

        while left_fueling_time:
            self.env.logger.info(f'[{self.data.name}]: Waiting for the pump with the fueling time {left_fueling_time}.')

            pump_parking_place_request = gas_station.fuel_pump_parking_place.request()
            yield pump_parking_place_request
            self.env.logger.info(f'[{self.data.name}]: Entering a fuel pump parking place.')

            pump_request = gas_station.fuel_pumps.request(priority=1)
            yield pump_request

            self.env.logger.info(f'[{self.data.name}]: Fueling.')
            self.env.logger.info(f'[STATION]: Getting a pump. {gas_station.fuel_pumps.count} of'
                                 f' {gas_station.fuel_pumps.capacity} pumps are allocated.')
            start_fueling_time = self.env.now

            if not hasattr(self.data, 'fueling_start_time'):
                self.data.fueling_start_time = start_fueling_time

            try:
                yield self.env.timeout(left_fueling_time)
                self.env.logger.info(f'[{self.data.name}]: Fueling succeeded.')
                self._fuel_gotten = self.data.expected_fueling_time
                left_fueling_time = 0
                self.data.fueling_end_time = self.env.now

            except simpy.Interrupt:
                fuel_got = self.env.now - start_fueling_time
                self._fuel_gotten += fuel_got
                if self._fuel_gotten > self.data.expected_fueling_time:
                    raise ValueError('Fuel gotten cannot be higher than fueling time')
                fuel_percentage = "{:.2f}".format(self._fuel_gotten / self.data.expected_fueling_time * 100)
                self.env.logger.info(f'[{self.data.name}]: Fueling has been interrupted.'
                                     f' Have {fuel_percentage}% of the fuel needed.')
                left_fueling_time -= fuel_got

            gas_station.fuel_pumps.release(pump_request)
            self.env.logger.info(f'[STATION]: Releasing a pump. {gas_station.fuel_pumps.count} of'
                                 f' {gas_station.fuel_pumps.capacity} pumps are allocated.')

            if left_fueling_time == 0:
                yield self.env.process(self.interact_with_the_cashier(gas_station=gas_station))
                if self.data.eating:
                    yield self.env.process(self.wait_and_take_the_food(gas_station=gas_station))
                gas_station.fuel_pump_parking_place.release(pump_parking_place_request)

        gas_station.parking_places.put(1)
        self.env.logger.info(f'[{self.data.name}]: Leaving the station.')
        return self.data

    def interact_with_the_cashier(self, gas_station: _GasStation) -> Generator[Event, Any, Any]:
        self.env.logger.info(f'[{self.data.name}]: Waiting at the counter.')
        self.env.logger.info(f'[STATION]: {gas_station.cashiers.count} of {gas_station.cashiers.capacity}'
                             f' cashiers are allocated.')

        with gas_station.cashiers.request(priority=1) as request:
            yield request
            self.data.interacting_with_cashier_start_time = self.env.now
            self.env.logger.info(f'[{self.data.name}]: Interacting with the cashier.')
            interacting_time = self._settings.interaction_with_cashier_time()
            yield self.env.timeout(interacting_time)
            self.data.interacting_with_cashier_end_time = self.env.now

        self.env.logger.info(f'[STATION]: {gas_station.cashiers.count} of {gas_station.cashiers.capacity}'
                             f' cashiers are allocated.')

    def wait_and_take_the_food(self, gas_station: _GasStation) -> Generator[Event, Any, Any]:
        food_preparation_time = self._settings.food_preparation_time()
        self.env.logger.info(f'[{self.data.name}]: Waiting for a hot-dog.')
        self.data.waiting_for_food_time_start_time = self.env.now
        yield self.env.timeout(food_preparation_time)

        self.env.logger.info(f'[STATION]: {gas_station.cashiers.count} of {gas_station.cashiers.capacity}'
                             f' cashiers are allocated.')

        with gas_station.cashiers.request(priority=0) as request:
            yield request
            yield self.env.timeout(self._settings.interaction_with_cashier_while_getting_food_time())
            self.env.logger.info(f'[{self.data.name}]: Got a hot-dog.')

        self.data.waiting_for_food_time_end_time = self.env.now
        self.env.logger.info(f'[STATION]: {gas_station.cashiers.count} of {gas_station.cashiers.capacity}'
                             f' cashiers are allocated.')
