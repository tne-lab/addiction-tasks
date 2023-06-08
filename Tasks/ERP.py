from enum import Enum
import random

import numpy as np

from Components.StimJim import StimJim
from Tasks.Task import Task
from Components.Stimmer import Stimmer

from Events.OEEvent import OEEvent
from Events.InputEvent import InputEvent


class ERP(Task):
    """@DynamicAttrs"""
    class States(Enum):
        START_RECORD = 0
        ERP = 1
        STOP_RECORD = 2

    class Inputs(Enum):
        ERP_STIM = 0
        SJ_RESPONSE = 1

    @staticmethod
    def get_components():
        return {
            'stim': [Stimmer],
            'setup': [StimJim]
        }

    # noinspection PyMethodMayBeStatic
    def get_constants(self):
        return {
            'ephys': False,
            'record_lockout': 4,
            'npulse': 100,
            'min_sep': 2.75,
            'jitter': 0.5,
            'stim_dur': [1800],
            'period': [1800],
            'amps': [[[60, -60], [0, 0]]],
            'pws': [[90, 90]],
            'stim_type': [[1, 3]],
            'trig_amp': 3.3,
            'trig_dur': 100
        }

    # noinspection PyMethodMayBeStatic
    def get_variables(self):
        return {
            "last_pulse_time": 0,
            "pulse_count": 0,
            "stim_last": False,
            "complete": False,
            "cur_jitter": 0,
            "cur_set": 1,
            "cur_params": None,
            "last_stim": None
        }

    def init_state(self):
        return self.States.START_RECORD

    def start(self):
        self.setup.parametrize(0, self.stim_type[0], self.stim_dur[0], self.period[0], np.array(self.amps[0]), self.pws[0])
        self.setup.trigger(0, 0)
        self.stim.parametrize(0, 1, self.trig_dur, self.trig_dur, np.array([[self.trig_amp]]), [self.trig_dur])
        if self.ephys:
            self.events.append(OEEvent(self, "startRecord", {"pre": "ERP"}))

    def handle_input(self) -> None:
        commands = self.setup.check()
        if len(commands) > 0:
            for command in commands:
                self.events.append(InputEvent(self, self.Inputs.SJ_RESPONSE, command))
                if command["command"] == "P":
                    self.cur_params = command
                elif command["command"] == "C":
                    self.last_stim = command

    def START_RECORD(self):
        if self.time_in_state() > self.record_lockout:
            self.cur_jitter = random.uniform(0, 1) * self.jitter
            self.change_state(self.States.ERP)

    def ERP(self):
        if self.cur_time - self.last_pulse_time > self.min_sep and self.cur_set > len(self.period):
            self.change_state(self.States.STOP_RECORD)
            if self.ephys:
                self.events.append(OEEvent(self, "stopRecord"))
        elif self.cur_time - self.last_pulse_time > self.min_sep + self.cur_jitter:
            self.last_pulse_time = self.cur_time
            self.stim.start(0)
            self.pulse_count += 1
            self.events.append(InputEvent(self, self.Inputs.ERP_STIM))
            self.cur_jitter = random.uniform(0, 1) * self.jitter
            if self.pulse_count == self.npulse:
                self.cur_set += 1
                self.pulse_count = 0
                if self.cur_set < len(self.period):
                    self.setup.parametrize(0, self.stim_type[self.cur_set], self.stim_dur[self.cur_set], self.period[self.cur_set], np.array(self.amps[self.cur_set]), self.pws[self.cur_set])

    def is_complete(self):
        return self.state == self.States.STOP_RECORD and self.time_in_state() > self.record_lockout