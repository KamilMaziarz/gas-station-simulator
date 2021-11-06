from functools import wraps
from pathlib import Path

import pandas as pd
import simpy
from simpy import Container
from simpy.resources.container import ContainerPut, ContainerGet
from simpy.resources.resource import Request, Release

_MONITORED_RESOURCES_PATH = Path('monitored_resources')


def save_monitored_data(method):
    @wraps(method)
    def inner(self, *args, **kwargs):
        method_return_value = method(self, *args, **kwargs)
        simulation_day = self._env.now // 60**2
        if simulation_day > self._day:
            _MONITORED_RESOURCES_PATH.mkdir(parents=True, exist_ok=True)
            file_path = (_MONITORED_RESOURCES_PATH / self.name).with_suffix('.csv')
            pd.DataFrame(self.data, columns=['time',  self.name]).to_csv(file_path, index=False)
            self._day += 1
        return method_return_value
    return inner


class _MonitoredResource(simpy.PreemptiveResource):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.data = []
        self._day = 0

    @save_monitored_data
    def request(self, *args, **kwargs) -> Request:
        self.data.append((self._env.now, self.count))
        return super().request()

    @save_monitored_data
    def release(self, request) -> Release:
        self.data.append((self._env.now, self.count))
        return super().release(request)


class MonitoredResource(_MonitoredResource):
    pass


class MonitoredPriorityResource(_MonitoredResource):
    pass


class MonitoredPreemptiveResource(_MonitoredResource):
    pass


class MonitoredContainer(Container):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.data = []
        self._day = 0
        _MONITORED_RESOURCES_PATH.mkdir(parents=True, exist_ok=True)

    @save_monitored_data
    def put(self, *args, **kwargs) -> ContainerPut:
        self.data.append((self._env.now, self.capacity - self.level))
        return super().put(*args, **kwargs)

    @save_monitored_data
    def get(self, *args, **kwargs) -> ContainerGet:
        self.data.append((self._env.now, self.capacity - self.level))
        return super().get(*args, **kwargs)
