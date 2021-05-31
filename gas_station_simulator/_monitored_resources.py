from pathlib import Path

import simpy
from simpy.resources.resource import Request, Release
import pandas as pd


class _MonitoredResource(simpy.PreemptiveResource):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.data = []
        self._day = 0

    def request(self, *args, **kwargs) -> Request:
        self.data.append((self._env.now, len(self.queue)))
        self._save_monitored_data()
        return super().request()

    def release(self, request) -> Release:
        self.data.append((self._env.now, len(self.queue)))
        self._save_monitored_data()
        return super().release(request)

    def _save_monitored_data(self) -> None:
        # save every simulation-hour
        monitored_resources = Path('monitored_resources')
        monitored_resources.mkdir(parents=True, exist_ok=True)
        simulation_day = self._env.now // (60*60)
        if simulation_day > self._day:
            file_path = (monitored_resources / self.name).with_suffix('.csv')
            pd.DataFrame(self.data, columns=['time', 'usage']).to_csv(file_path, index=False)
            self._day = simulation_day


class MonitoredResource(_MonitoredResource):
    pass


class MonitoredPriorityResource(_MonitoredResource):
    pass


class MonitoredPreemptiveResource(_MonitoredResource):
    pass
