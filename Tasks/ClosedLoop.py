from enum import Enum

import numpy as np

from Events import PybEvents
from Tasks.Task import Task
from Components.BinaryInput import BinaryInput
from Components.Stimmer import Stimmer
from Components.StimJim import StimJim


class ClosedLoop(Task):
    """@DynamicAttrs"""
    class States(Enum):
        START_RECORD = 0
        CLOSED_LOOP = 1
        STOP_RECORD = 2

    class Events(Enum):
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
            'complete': False
        }

    def init_state(self):
        return self.States.START_RECORD

    def start(self):
        self.setup.parametrize(0, self.stim_type, self.stim_dur, self.period, np.array(self.amps), self.pws)
        self.setup.trigger(0, 0)
        self.stim.parametrize(0, 1, self.trig_dur, self.trig_dur, np.array([[self.trig_amp]]), [self.trig_dur])
        self.sham.parametrize(0, 1, self.trig_dur, self.trig_dur, np.array([[self.trig_amp]]), [self.trig_dur])
        if self.ephys:
            self.log_event(PybEvents.OEEvent(self, "startRecord", {"pre": "ClosedLoop"}))

    def stop(self):
        if self.ephys:
            self.log_event(PybEvents.OEEvent(self.metadata["chamber"], "stopRecord"))

    def all_states(self, event: PybEvents.PybEvent) -> bool:
        if isinstance(event, PybEvents.TimeoutEvent) and event.name == "task_complete":
            self.complete = True
            return True
        return False

    def START_RECORD(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            self.set_timeout("start_record", self.record_lockout)
        if isinstance(event, PybEvents.TimeoutEvent) and event.name == "start_record":
            self.change_state(self.States.CLOSED_LOOP)

    def CLOSED_LOOP(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            self.set_timeout("closed_loop_complete", self.duration)
        elif isinstance(event, PybEvents.TimeoutEvent) and event.name == "closed_loop_complete":
            self.change_state(self.States.STOP_RECORD)
        elif isinstance(event, PybEvents.ComponentChangedEvent) and event.comp == self.threshold:
            if self.cur_time - self.last_pulse_time > self.min_pulse_separation:
                if self.threshold.state:
                    if not self.stim_last:
                        self.log_event(PybEvents.InfoEvent(self, self.Events.STIM))
                        self.stim.start(0)
                        self.pulse_count += 1
                    else:
                        self.log_event(PybEvents.InfoEvent(self, self.Events.SHAM))
                        self.sham.start(0)
                    self.stim_last = not self.stim_last

    def STOP_RECORD(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            self.set_timeout("stop_record", self.record_lockout)
        if isinstance(event, PybEvents.TimeoutEvent) and event.name == "stop_record":
            self.complete = True
