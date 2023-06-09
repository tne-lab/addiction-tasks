import random
from enum import Enum

from Components.BinaryInput import BinaryInput
from Components.Toggle import Toggle
from Components.TimedToggle import TimedToggle
from Tasks import TaskEvents

from Tasks.Task import Task

from ..GUIs.SetShiftGUI import SetShiftGUI


class SetShift(Task):
    """@DynamicAttrs"""
    class States(Enum):
        INITIATION = 0
        RESPONSE = 1
        INTER_TRIAL_INTERVAL = 2

    class Inputs(Enum):
        FRONT_ENTERED = 2
        FRONT_EXIT = 3
        MIDDLE_ENTERED = 4
        MIDDLE_EXIT = 5
        REAR_ENTERED = 6
        REAR_EXIT = 7

    @staticmethod
    def get_components():
        return {
            'nose_pokes': [BinaryInput, BinaryInput, BinaryInput],
            'nose_poke_lights': [Toggle, Toggle, Toggle],
            'food': [TimedToggle],
            'house_light': [Toggle],
            'chamber_light': [Toggle]
        }

    # noinspection PyMethodMayBeStatic
    def get_constants(self):
        return {
            'max_duration': 90,
            'inter_trial_interval': 7,
            'response_duration': 3,
            'n_random_start': 10,
            'n_random_end': 5,
            'rule_sequence': [0, 1, 0, 2, 0, 1, 0, 2],
            'correct_to_switch': 5,
            'light_sequence': random.sample([True for _ in range(27)] + [False for _ in range(28)], 55),
            'dispense_time': 0.7
        }

    # noinspection PyMethodMayBeStatic
    def get_variables(self):
        return {
            'cur_trial': 0,
            'cur_rule': 0,
            'cur_block': 0,
            'pokes': []
        }

    def init_state(self):
        return self.States.INITIATION

    def init(self):
        self.house_light.toggle(True)
        self.chamber_light.toggle(True)

    def clear(self):
        self.house_light.toggle(False)
        self.chamber_light.toggle(False)

    def start(self):
        self.set_timeout("task_complete", self.max_duration * 60)
        self.chamber_light.toggle(False)

    def stop(self):
        self.chamber_light.toggle(True)
        for i in range(3):
            self.nose_poke_lights[i].toggle(False)

    def all_states(self, event: TaskEvents.TaskEvent) -> bool:
        if isinstance(event, TaskEvents.TimeoutEvent) and event.name == "task_complete":
            self.complete = True
            return True
        elif isinstance(event, TaskEvents.GUIEvent) and event.event == SetShiftGUI.Inputs.GUI_PELLET:
            self.food.toggle(self.dispense_time)
            return True
        return False

    def INITIATION(self, event: TaskEvents.TaskEvent):
        if isinstance(event, TaskEvents.StateEnterEvent):
            self.nose_poke_lights[1].toggle(True)
        elif isinstance(event, TaskEvents.ComponentChangedEvent) and event.comp is self.nose_pokes[1] and event.comp:
            self.nose_poke_lights[1].toggle(False)
            self.change_state(self.States.RESPONSE, {"light_location": self.light_sequence[self.cur_trial]})

    def RESPONSE(self, event: TaskEvents.TaskEvent):
        metadata = {}
        if isinstance(event, TaskEvents.StateEnterEvent):
            if self.light_sequence[self.cur_trial]:
                self.nose_poke_lights[2].toggle(True)
            else:
                self.nose_poke_lights[0].toggle(True)
            self.set_timeout("response_timeout", self.response_duration)
        elif isinstance(event, TaskEvents.ComponentChangedEvent) and (event.comp is self.nose_pokes[0] or event.comp is self.nose_pokes[2]) and event.comp:
            if self.cur_trial < self.n_random_start or self.cur_trial >= self.n_random_start + self.correct_to_switch * len(
                    self.rule_sequence):
                if random.random() < 0.5:
                    self.food.toggle(self.dispense_time)
                    metadata["accuracy"] = "correct"
                else:
                    metadata["accuracy"] = "incorrect"
                self.cur_trial += 1
                metadata["rule_index"] = -1
            else:
                metadata["rule"] = self.rule_sequence[self.cur_rule]
                metadata["cur_block"] = self.cur_block
                metadata["rule_index"] = self.cur_rule
                if self.rule_sequence[self.cur_rule] == 0:
                    if (event.comp is self.nose_pokes[0] and not self.light_sequence[self.cur_trial]) or (
                            event.comp is self.nose_pokes[2] and self.light_sequence[self.cur_trial]):
                        self.correct()
                        metadata["accuracy"] = "correct"
                    else:
                        self.cur_trial -= self.cur_block
                        self.cur_block = 0
                        metadata["accuracy"] = "incorrect"
                elif self.rule_sequence[self.cur_rule] == 1:
                    if event.comp is self.nose_pokes[0]:
                        self.correct()
                        metadata["accuracy"] = "correct"
                    else:
                        self.cur_trial -= self.cur_block
                        self.cur_block = 0
                        metadata["accuracy"] = "incorrect"
                elif self.rule_sequence[self.cur_rule] == 2:
                    if event.comp is self.nose_pokes[2]:
                        self.correct()
                        metadata["accuracy"] = "correct"
                    else:
                        self.cur_trial -= self.cur_block
                        self.cur_block = 0
                        metadata["accuracy"] = "incorrect"
            self.change_state(self.States.INTER_TRIAL_INTERVAL, metadata)
        elif isinstance(event, TaskEvents.TimeoutEvent) and event.name == "response_timeout":
            if self.cur_trial < self.n_random_start or self.cur_trial >= self.n_random_start + self.correct_to_switch * len(
                    self.rule_sequence):
                metadata["rule_index"] = -1
            else:
                metadata["rule"] = self.rule_sequence[self.cur_rule]
                metadata["cur_block"] = self.cur_block
                metadata["rule_index"] = self.cur_rule
            metadata["accuracy"] = "incorrect"
            metadata["response"] = "none"
            self.change_state(self.States.INTER_TRIAL_INTERVAL, metadata)
        elif isinstance(event, TaskEvents.StateExitEvent):
            self.nose_poke_lights[0].toggle(False)
            self.nose_poke_lights[2].toggle(False)

    def INTER_TRIAL_INTERVAL(self, event: TaskEvents.TaskEvent):
        if isinstance(event, TaskEvents.StateEnterEvent):
            self.set_timeout("iti_timeout", self.inter_trial_interval)
        elif isinstance(event, TaskEvents.TimeoutEvent) and event.name == "iti_timeout":
            self.nose_poke_lights[1].toggle(True)
            self.change_state(self.States.INITIATION)

    def is_complete(self):
        return self.cur_trial == self.n_random_start + self.n_random_end + self.correct_to_switch * len(self.rule_sequence)

    def correct(self):
        self.food.toggle(self.dispense_time)
        if self.cur_block + 1 == self.correct_to_switch:
            self.cur_rule += 1
            self.cur_block = 0
        else:
            self.cur_block += 1
        self.cur_trial += 1
