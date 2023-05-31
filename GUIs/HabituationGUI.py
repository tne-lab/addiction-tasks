from enum import Enum
from typing import List
from types import MethodType

from Elements.Element import Element
from Elements.ButtonElement import ButtonElement
from Elements.InfoBoxElement import InfoBoxElement
from Events.InputEvent import InputEvent
from GUIs.GUI import GUI


class HabituationGUI(GUI):
    class Inputs(Enum):
        GUI_FEED = 0

    def __init__(self, task_gui, task):
        super().__init__(task_gui, task)
        self.info_boxes = []

        def feed_mouse_up(self, _):
            self.clicked = False
            task.reset = True
            task.events.append(InputEvent(task, HabituationGUI.Inputs.GUI_FEED))

        def pellets_text(self):
            return [str(task.food.count)]

        def time_in_trial_text(self):
            return [str(round(task.time_elapsed() / 60, 2))]

        self.feed_button = ButtonElement(self, 175, 530, 150, 60, "FEED", f_size=28)
        self.feed_button.mouse_up = MethodType(feed_mouse_up, self.feed_button)
        pellets = InfoBoxElement(self, 200, 440, 100, 30, "PELLETS", 'BOTTOM', ['0'], f_size=28)
        pellets.get_text = MethodType(pellets_text, pellets)
        self.info_boxes.append(pellets)
        time_in_trial = InfoBoxElement(self, 375, 580, 100, 30, "TIME", 'BOTTOM', ['0'], f_size=28)
        time_in_trial.get_text = MethodType(time_in_trial_text, time_in_trial)
        self.info_boxes.append(time_in_trial)

    def get_elements(self) -> List[Element]:
        return [self.feed_button, *self.info_boxes]
