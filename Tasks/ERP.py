from enum import Enum
import random

import numpy as np

from Components.StimJim import StimJim
from Events import PybEvents
from Tasks.Task import Task
from Components.Stimmer import Stimmer


class ERP(Task):
    """@DynamicAttrs"""
    class States(Enum):
        START_RECORD = 0
        ERP = 1
        STOP_RECORD = 2

    class Events(Enum):
        STIM = 0
        SJ_RESPONSE = 1
        SHAM = 2

    @staticmethod
    def get_components():
        return {
            'stim': [Stimmer],
            'sham': [Stimmer],
            'setup': [StimJim]
        }

    # noinspection PyMethodMayBeStatic
    def get_constants(self):
        return {
            'use_sham': False,
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
            "pulse_count": 0,
            "complete": False,
            "cur_jitter": 0,
            "cur_set": 1,
            "cur_params": None,
            "last_stim": None,
            "sham_next": True
        }

    def init_state(self):
        return self.States.START_RECORD

    def start(self):
        self.setup.parametrize(0, self.stim_type[0], self.stim_dur[0], self.period[0], np.array(self.amps[0]), self.pws[0])
        self.setup.trigger(0, 0)
        self.stim.parametrize(0, 1, self.trig_dur, self.trig_dur, np.array([[self.trig_amp]]), [self.trig_dur])
        if self.use_sham:
            self.sham.parametrize(0, 1, self.trig_dur, self.trig_dur, np.array([[self.trig_amp]]), [self.trig_dur])
        if self.ephys:
            self.log_event(PybEvents.OEEvent(self, "startRecord", {"pre": "ERP"}))

    def stop(self) -> None:
        if self.ephys:
            self.log_event(PybEvents.OEEvent(self, "stopRecord"))

    def all_states(self, event: PybEvents.PybEvent) -> bool:
        if isinstance(event, PybEvents.ComponentChangedEvent) and event.comp is self.setup:
            for command in self.setup.commands:
                self.events.append(PybEvents.InfoEvent(self, self.Events.SJ_RESPONSE, command))
                if command["command"] == "P":
                    self.cur_params = command
                elif command["command"] == "C":
                    self.last_stim = command
            return True
        return False

    def START_RECORD(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            self.set_timeout("start_record", self.record_lockout)
        if isinstance(event, PybEvents.TimeoutEvent) and event.name == "start_record":
            self.change_state(self.States.ERP)

    def ERP(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            self.cur_jitter = random.uniform(0, 1) * self.jitter
            self.set_timeout("erp", self.cur_jitter + self.min_sep)
        if isinstance(event, PybEvents.TimeoutEvent) and event.name == "erp":
            if self.cur_set > len(self.period):
                self.change_state(self.States.STOP_RECORD)
            else:
                if self.use_sham and self.sham_next:
                    self.sham.start(0)
                    self.sham_next = False
                    self.log_event(PybEvents.InfoEvent(self, self.Events.SHAM))
                else:
                    self.stim.start(0)
                    self.pulse_count += 1
                    self.sham_next = True
                    self.log_event(PybEvents.InfoEvent(self, self.Events.STIM))
                self.cur_jitter = random.uniform(0, 1) * self.jitter
                if self.pulse_count == self.npulse:
                    self.pulse_count = 0
                    if self.cur_set < len(self.period):
                        self.setup.parametrize(0, self.stim_type[self.cur_set], self.stim_dur[self.cur_set], self.period[self.cur_set], np.array(self.amps[self.cur_set]), self.pws[self.cur_set])
                    self.cur_set += 1
                self.set_timeout("erp", self.cur_jitter + self.min_sep)

    def STOP_RECORD(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            self.set_timeout("stop_record", self.record_lockout)
        if isinstance(event, PybEvents.TimeoutEvent) and event.name == "stop_record":
            self.complete = True
