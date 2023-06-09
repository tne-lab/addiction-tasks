from enum import Enum

import numpy as np

from Components.TimedToggle import TimedToggle
from Tasks.Task import Task
from Components.BinaryInput import BinaryInput
from Components.StimJim import StimJim
from Events.InputEvent import InputEvent

from Events.OEEvent import OEEvent


class ClosedLoop(Task):
    """@DynamicAttrs"""
    class States(Enum):
        START_RECORD = 0
        CLOSED_LOOP = 1
        STOP_RECORD = 2

    class Inputs(Enum):
        STIM = 1
        SHAM = 2

    @staticmethod
    def get_components():
        return {
            'threshold': [BinaryInput],
            'stim': [StimJim],
            'stim_toggle': [TimedToggle],
            'sham_toggle': [TimedToggle]
        }

    # noinspection PyMethodMayBeStatic
    def get_constants(self):
        return {
            'ephys': False,
            'record_lockout': 4,
            'duration': 30,
            'min_pulse_separation': 2,
            'stim_dur': 1800,
            'period': 1800,
            'amps': ([[100, -100], [0, 0]]),
            'pws': [100, 100],
            'channel_settings': [1,3],
            'trig_dur': 0.005
        }

    # noinspection PyMethodMayBeStatic
    def get_variables(self):
        return {
            'last_pulse_time': 0,
            'pulse_count': 0,
            'stim_last': False,
            'complete': False,
            'thr': None
        }

    def init_state(self):
        return self.States.START_RECORD

    def start(self):
        self.stim.parametrize(0, self.channel_settings, self.stim_dur, self.period, np.array(self.amps), self.pws)
        if self.ephys:
            self.events.append(OEEvent(self, "startRecord", {"pre": "ClosedLoop"}))

    def all_states(self) -> None:
        self.thr = self.threshold.check()

    def START_RECORD(self):
        if self.time_in_state() > self.record_lockout:
            self.change_state(self.States.CLOSED_LOOP)

    def CLOSED_LOOP(self):
        if self.cur_time - self.last_pulse_time > self.min_pulse_separation and self.time_in_state() > self.duration * 60:
            self.change_state(self.States.STOP_RECORD)
            if self.ephys:
                self.events.append(OEEvent(self, "stopRecord"))
        else:
            if self.cur_time - self.last_pulse_time > self.min_pulse_separation:
                if self.thr == BinaryInput.ENTERED:
                    if not self.stim_last:
                        self.stim_toggle.toggle(self.trig_dur)
                        self.stim.start(0)
                        self.pulse_count += 1
                    else:
                        self.sham_toggle.toggle(self.trig_dur)
                    self.stim_last = not self.stim_last

    def is_complete(self):
        return self.state == self.States.STOP_RECORD and self.time_in_state() > self.record_lockout
