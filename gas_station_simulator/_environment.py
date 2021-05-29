import logging
from typing import Type

import simpy

from gas_station_simulator._utils import _get_time_string


class _EnvironmentLoggerFormatter(logging.Formatter):
    def __init__(self, environment: simpy.Environment, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._env = environment

    def formatTime(self, record, datefmt=None) -> str:
        return _get_time_string(time=self._env.now)


class _SimulationEnvironment(simpy.Environment):
    def __init__(self, formatter: Type[_EnvironmentLoggerFormatter] = _EnvironmentLoggerFormatter, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.logger = self._initialize_logger(formatter)
        self.logger.info('[ENVIRONMENT] Environment set.')

    def _initialize_logger(self, formatter: Type[_EnvironmentLoggerFormatter]) -> logging.Logger:
        logger = logging.getLogger('gas_station')
        logger.setLevel(logging.INFO)

        formatter = formatter(self, '%(asctime)s: %(message)s')

        ch = logging.StreamHandler()
        ch.setFormatter(formatter)

        fh = logging.FileHandler('logs.log')
        fh.setFormatter(formatter)

        logger.addHandler(ch)
        logger.addHandler(fh)
        return logger
