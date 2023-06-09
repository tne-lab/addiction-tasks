from enum import Enum

from Tasks.Task import Task

from Components.BinaryInput import BinaryInput
from Components.TimedToggle import TimedToggle
from Components.Toggle import Toggle
from Events.InputEvent import InputEvent
from Tasks.TaskEvents import TaskEvent, ComponentChangedEvent, TimeoutEvent, GUIEvent

from ..GUIs.SetShiftTrainingGUI import SetShiftTrainingGUI


class SetShiftTraining(Task):
    """@DynamicAttrs"""
    class States(Enum):
        INITIATION = 0
        RESPONSE = 1
        INTER_TRIAL_INTERVAL = 2

    class Inputs(Enum):
        MIDDLE_ENTERED = 0
        MIDDLE_EXIT = 1
        FRONT_ENTERED = 2
        FRONT_EXIT = 3
        REAR_ENTERED = 4
        REAR_EXIT = 5
        RESET_PRESSED = 6

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

    # noinspection PyMethodMayBeStatic
    def get_constants(self):
        return {
            'dispense_time': 0.7,
            'training_stage': 'middle',
            'max_duration': 90,
            'pokes_to_complete': 20,
            'inter_trial_interval': 7,
            'timeout': 20,
            'light_seq': [0, 1, 0, 1, 1, 0, 0, 1, 1, 0]
        }

    # noinspection PyMethodMayBeStatic
    def get_variables(self):
        return {
            "pokes": 0,
            'poke_vec': [],
            "reset": False,
            "gui_init": False
        }

    def init_state(self):
        return self.States.INTER_TRIAL_INTERVAL, self.inter_trial_interval

    def init(self):
        self.house_light.toggle(True)
        self.chamber_light.toggle(True)

    def clear(self):
        self.house_light.toggle(False)
        self.chamber_light.toggle(False)

    def start(self):
        self.task_timeout.start(self.max_duration * 60)
        self.chamber_light.toggle(False)

    def stop(self):
        self.chamber_light.toggle(True)
        for i in range(3):
            self.nose_poke_lights[i].toggle(False)

    def all_states(self, event: TaskEvent) -> None:
        if isinstance(event, ComponentChangedEvent):
            if event.comp is self.feed_press:
                if event.comp.state:
                    self.reset = True
                    self.events.append(InputEvent(self, self.Inputs.RESET_PRESSED))
            else:
                for i in range(3):
                    if event.comp is self.nose_pokes[i]:
                        if event.comp.state:
                            if i == 0:
                                self.events.append(InputEvent(self, self.Inputs.FRONT_ENTERED))
                            elif i == 1:
                                self.events.append(InputEvent(self, self.Inputs.MIDDLE_ENTERED))
                            elif i == 2:
                                self.events.append(InputEvent(self, self.Inputs.REAR_ENTERED))
                        else:
                            if i == 0:
                                self.events.append(InputEvent(self, self.Inputs.FRONT_EXIT))
                            elif i == 1:
                                self.events.append(InputEvent(self, self.Inputs.MIDDLE_EXIT))
                            elif i == 2:
                                self.events.append(InputEvent(self, self.Inputs.REAR_EXIT))

    def RESPONSE(self, event: TaskEvent):
        if isinstance(event, TimeoutEvent):
            self.nose_poke_lights[0].toggle(False)
            self.nose_poke_lights[2].toggle(False)
            self.pokes = 0
            self.change_state(self.States.INTER_TRIAL_INTERVAL)
        elif isinstance(event, ComponentChangedEvent) and (event.comp is self.nose_pokes[0] or event.comp is self.nose_pokes[2]) and event.comp:
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
            self.nose_poke_lights[0].toggle(False)
            self.nose_poke_lights[2].toggle(False)
            self.change_state(self.States.INTER_TRIAL_INTERVAL)
        elif isinstance(event, GUIEvent) and event.event == SetShiftTrainingGUI.Inputs.GUI_SHAPE:
            self.pokes = 0
            self.food.toggle(self.dispense_time)
            self.nose_poke_lights[0].toggle(False)
            self.nose_poke_lights[2].toggle(False)
            self.change_state(self.States.INTER_TRIAL_INTERVAL)

    def INITIATION(self, event: TaskEvent):
        if (isinstance(event, ComponentChangedEvent) and event.comp is self.nose_pokes[1]) \
                or (isinstance(event, GUIEvent) and event.event == SetShiftTrainingGUI.Inputs.GUI_INIT):
            if isinstance(event, GUIEvent):
                self.pokes = 0
            self.nose_poke_lights[1].toggle(False)
            if self.training_stage == 'middle':
                self.food.toggle(self.dispense_time)
                self.pokes += 1
                self.change_state(self.States.INTER_TRIAL_INTERVAL)
            else:
                self.nose_poke_lights[2*self.light_seq[self.pokes]].toggle(True)
                self.change_state(self.States.RESPONSE)
        elif isinstance(event, GUIEvent) and event.event == SetShiftTrainingGUI.Inputs.GUI_SHAPE:
            self.pokes = 0
            self.food.toggle(self.dispense_time)
            self.nose_poke_lights[1].toggle(False)
            self.change_state(self.States.INTER_TRIAL_INTERVAL)

    def INTER_TRIAL_INTERVAL(self, event: TaskEvent):
        if isinstance(event, TimeoutEvent):
            self.nose_poke_lights[1].toggle(True)
            self.change_state(self.States.INITIATION)

    def is_complete(self):
        return self.pokes == self.pokes_to_complete
