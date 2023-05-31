from enum import Enum

from Tasks.Task import Task

from Components.TimedToggle import TimedToggle
from Components.Toggle import Toggle


class Habituation(Task):
    """@DynamicAttrs"""

    class States(Enum):
        BEGIN = 0
        DISPENSE = 1
        END = 2

    @staticmethod
    def get_components():
        return {
            'food': [TimedToggle],
            'house_light': [Toggle],
            'chamber_light': [Toggle]
        }

    # noinspection PyMethodMayBeStatic
    def get_constants(self):
        return {
            'begin_delay': 10,
            'inter_dispense_interval': 3,
            'dispense_time': 0.7,
            'pellets': 20,
            'end_delay': 1130
        }

    def init_state(self):
        return self.States.BEGIN

    def init(self):
        self.house_light.toggle(True)
        self.chamber_light.toggle(True)

    def clear(self):
        self.house_light.toggle(False)
        self.chamber_light.toggle(False)

    def start(self):
        self.chamber_light.toggle(False)

    def stop(self):
        self.chamber_light.toggle(True)

    def BEGIN(self):
        if self.time_in_state() > self.begin_delay:
            self.food.toggle(self.dispense_time)
            self.change_state(self.States.DISPENSE)

    def DISPENSE(self):
        if self.time_in_state() > self.inter_dispense_interval:
            self.food.toggle(self.dispense_time)
            if self.food.count < self.pellets:
                self.change_state(self.States.DISPENSE)
            else:
                self.change_state(self.States.END)

    def is_complete(self):
        return self.state == self.States.END and self.time_in_state() > self.end_delay
