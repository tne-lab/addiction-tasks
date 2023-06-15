from enum import Enum

from Events import PybEvents
from Tasks.Task import Task

from Components.TimedToggle import TimedToggle
from Components.Toggle import Toggle

from ..GUIs.HabituationGUI import HabituationGUI


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

    def all_states(self, event: PybEvents.PybEvent) -> bool:
        if isinstance(event, PybEvents.GUIEvent) and event.event == HabituationGUI.Events.GUI_FEED:
            self.food.toggle(self.dispense_time)
            return True
        return False

    def BEGIN(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            self.set_timeout("begin_delay", self.begin_delay)
        elif isinstance(event, PybEvents.TimeoutEvent) and event.name == "begin_delay":
            self.change_state(self.States.DISPENSE)

    def DISPENSE(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            self.set_timeout("dispense", self.inter_dispense_interval)
        elif isinstance(event, PybEvents.TimeoutEvent) and event.name == "dispense":
            self.food.toggle(self.dispense_time)
            if self.food.count < self.pellets:
                self.change_state(self.States.DISPENSE)
            else:
                self.change_state(self.States.END)

    def END(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            self.set_timeout("end", self.end_delay)
        elif isinstance(event, PybEvents.TimeoutEvent) and event.name == "end":
            self.complete = True
