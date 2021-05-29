import simpy

from gas_station_simulator._settings import SimulationSettings
from gas_station_simulator._environment import _SimulationEnvironment
from gas_station_simulator._utils import _get_time_string


class _GasStation:
    def __init__(self, environment: _SimulationEnvironment, settings: SimulationSettings):
        self.env = environment
        self._settings = settings

        self.fuel_pumps = simpy.PreemptiveResource(environment, settings.pumps_quantity)
        self.cashiers = simpy.PriorityResource(environment, settings.cashier_quantity)
        self.parking_places = simpy.Container(
            environment,
            init=settings.pumps_quantity * 4,
            capacity=settings.pumps_quantity * 4,
        )
        environment.process(self._break_the_pump())

    def _break_the_pump(self):
        while True:
            working_time = self._settings.pump_working_time()
            self.env.logger.info(f'[PUMP BREAK]: A pump will break in'
                                 f' {_get_time_string(working_time, print_days=False)}')
            yield self.env.timeout(working_time)
            self.env.logger.info(f'{self.fuel_pumps.count} of {self.fuel_pumps.capacity} pumps are allocated.')
            if self.fuel_pumps.count == self.fuel_pumps.capacity:
                self.env.logger.info('[PUMP BREAK]: Interrupting the fueling process since all of the pumps are'
                                     ' allocated.')
            with self.fuel_pumps.request(priority=-1) as request:
                yield request
                outage_time = self._settings.pump_outage_time()
                self.env.logger.info(f'[PUMP BREAK]: One of the pumps has broken and will be unavailable for'
                                     f' {_get_time_string(working_time, print_days=False)}.')
                yield self.env.timeout(outage_time)
                print(f'[PUMP BREAK]: The pump is repaired.')
