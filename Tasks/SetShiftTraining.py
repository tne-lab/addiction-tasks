from enum import Enum

from Events import PybEvents
from Tasks.Task import Task

from Components.BinaryInput import BinaryInput
from Components.TimedToggle import TimedToggle
from Components.Toggle import Toggle


class SetShiftTraining(Task):
    """@DynamicAttrs"""
    class States(Enum):
        INITIATION = 0
        RESPONSE = 1
        INTER_TRIAL_INTERVAL = 2

    @staticmethod
    def get_components():
        return {
            'nose_pokes': [BinaryInput, BinaryInput, BinaryInput],
            'nose_poke_lights': [Toggle, Toggle, Toggle],
            'feed_press': [BinaryInput],
            'food': [TimedToggle],
            'house_light': [Toggle],
            'chamber_light': [Toggle]
        }

    @staticmethod
    def get_constants():
        return {
            'dispense_time': 0.7,
            'training_stage': 'middle',
            'max_duration': 90,
            'pokes_to_complete': 20,
            'inter_trial_interval': 7,
            'timeout': 20,
            'light_seq': [0, 1, 0, 1, 1, 0, 0, 1, 1, 0]
        }

    @staticmethod
    def get_variables():
        return {
            "pokes": 0
        }

    def init_state(self):
        return self.States.INTER_TRIAL_INTERVAL

    def init(self):
        self.house_light.toggle(True)
        self.chamber_light.toggle(True)

    def clear(self):
        self.house_light.toggle(False)
        self.chamber_light.toggle(False)

    def start(self):
        self.set_timeout("response_timeout", self.max_duration * 60)
        self.chamber_light.toggle(False)

    def stop(self):
        self.chamber_light.toggle(True)
        for i in range(3):
            self.nose_poke_lights[i].toggle(False)

    def RESPONSE(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            self.nose_poke_lights[2 * self.light_seq[self.pokes]].toggle(True)
            self.set_timeout("response_timeout", self.timeout)
        elif isinstance(event, PybEvents.TimeoutEvent) and event.name == "response_timeout":
            self.change_state(self.States.INTER_TRIAL_INTERVAL)
        elif isinstance(event, PybEvents.ComponentChangedEvent) and (event.comp is self.nose_pokes[0] or event.comp is self.nose_pokes[2]) and event.comp.state:
            if event.comp is self.nose_pokes[0]:
                if (self.nose_poke_lights[0].get_state() and self.training_stage == 'light') or self.training_stage == 'front':
                    self.food.toggle(self.dispense_time)
                    self.pokes += 1
                else:
                    self.pokes = 0
            elif event.comp is self.nose_pokes[2]:
                if (self.nose_poke_lights[2].get_state() and self.training_stage == 'light') or self.training_stage == 'rear':
                    self.food.toggle(self.dispense_time)
                    self.pokes += 1
                else:
                    self.pokes = 0
            self.change_state(self.States.INTER_TRIAL_INTERVAL)
        elif isinstance(event, PybEvents.GUIEvent) and event.name == "GUI_SHAPE":
            self.pokes = 0
            self.food.toggle(self.dispense_time)
            self.change_state(self.States.INTER_TRIAL_INTERVAL)
        elif isinstance(event, PybEvents.StateExitEvent):
            self.nose_poke_lights[0].toggle(False)
            self.nose_poke_lights[2].toggle(False)

    def INITIATION(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            self.nose_poke_lights[1].toggle(True)
        elif (isinstance(event, PybEvents.ComponentChangedEvent) and event.comp is self.nose_pokes[1]) \
                or (isinstance(event, PybEvents.GUIEvent) and event.name == "GUI_INIT"):
            if isinstance(event, PybEvents.GUIEvent):
                self.pokes = 0
            if self.training_stage == 'middle':
                self.food.toggle(self.dispense_time)
                self.pokes += 1
                self.change_state(self.States.INTER_TRIAL_INTERVAL)
            else:
                self.change_state(self.States.RESPONSE)
        elif isinstance(event, PybEvents.GUIEvent) and event.name == "GUI_SHAPE":
            self.pokes = 0
            self.food.toggle(self.dispense_time)
            self.change_state(self.States.INTER_TRIAL_INTERVAL)
        elif isinstance(event, PybEvents.StateExitEvent):
            self.nose_poke_lights[1].toggle(False)

    def INTER_TRIAL_INTERVAL(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            self.set_timeout("iti_timeout", self.inter_trial_interval)
        elif isinstance(event, PybEvents.TimeoutEvent) and event.name == "iti_timeout":
            self.change_state(self.States.INITIATION)

    def is_complete(self):
        return self.pokes == self.pokes_to_complete
