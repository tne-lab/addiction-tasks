from enum import Enum

import numpy as np
from Tasks.Task import Task
from Components.BinaryInput import BinaryInput
from Components.Stimmer import Stimmer
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
        STIM = 0
        SHAM = 1

    @staticmethod
    def get_components():
        return {
            'threshold': [BinaryInput],
            'stim': [Stimmer],
            'sham': [Stimmer],
            'setup': [StimJim]
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
            'stim_type': [1, 3],
            'trig_amp': 3.3,
            'trig_dur': 100
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
        self.setup.parametrize(0, self.stim_type, self.stim_dur, self.period, np.array(self.amps), self.pws)
        self.setup.trigger(0, 0)
        self.stim.parametrize(0, 1, self.trig_dur, self.trig_dur, np.array([[self.trig_amp]]), [self.trig_dur])
        self.sham.parametrize(0, 1, self.trig_dur, self.trig_dur, np.array([[self.trig_amp]]), [self.trig_dur])
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
                        self.events.append(InputEvent(self, self.Inputs.STIM))
                        self.stim.start(0)
                        self.pulse_count += 1
                    else:
                        self.events.append(InputEvent(self, self.Inputs.SHAM))
                        self.sham.start(0)
                    self.stim_last = not self.stim_last

    def is_complete(self):
        return self.state == self.States.STOP_RECORD and self.time_in_state() > self.record_lockout
