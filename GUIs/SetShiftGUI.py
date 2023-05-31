from typing import List
from types import MethodType
from enum import Enum

from Elements.CircleLightElement import CircleLightElement
from Elements.Element import Element
from Elements.NosePokeElement import NosePokeElement
from Elements.ButtonElement import ButtonElement
from Elements.InfoBoxElement import InfoBoxElement
from Events.InputEvent import InputEvent
from GUIs.GUI import GUI


class SetShiftGUI(GUI):
    class Inputs(Enum):
        GUI_PELLET = 0

    def __init__(self, task_gui, task):
        super().__init__(task_gui, task)
        self.np_lights = []
        self.np_inputs = []
        self.info_boxes = []

        def feed_mouse_up(self, _):
            self.clicked = False
            task.food.toggle(task.dispense_time)
            task.events.append(InputEvent(task, SetShiftGUI.Inputs.GUI_PELLET))

        def pellets_text(self):
            return [str(task.food.count)]

        def trial_count_text(self):
            return [str(task.cur_trial+1)]

        def time_in_trial_text(self):
            return [str(round(task.time_elapsed() / 60, 2))]

        for i in range(3):
            npl = CircleLightElement(self, 50 + (i+1)*(25+60), 60, 30, comp=task.nose_poke_lights[i])
            self.np_lights.append(npl)
            npi = NosePokeElement(self, 50 + (i+1) * (25 + 60), 150, 30, comp=task.nose_pokes[i])
            self.np_inputs.append(npi)
        self.feed_button = ButtonElement(self, 200, 530, 100, 40, "FEED", f_size=28)
        self.feed_button.mouse_up = MethodType(feed_mouse_up, self.feed_button)
        pellets = InfoBoxElement(self, 200, 440, 100, 30, "PELLETS", 'BOTTOM', ['0'], f_size=28)
        pellets.get_text = MethodType(pellets_text, pellets)
        self.info_boxes.append(pellets)
        time_in_trial = InfoBoxElement(self, 375, 580, 100, 30, "TIME", 'BOTTOM', ['0'], f_size=28)
        time_in_trial.get_text = MethodType(time_in_trial_text, time_in_trial)
        self.info_boxes.append(time_in_trial)
        trial_count = InfoBoxElement(self, 375, 500, 100, 30, "TRIAL", 'BOTTOM', ['0'], f_size=28)
        trial_count.get_text = MethodType(trial_count_text, trial_count)
        self.info_boxes.append(trial_count)

    def get_elements(self) -> List[Element]:
        return [*self.np_lights, *self.np_inputs, self.feed_button, *self.info_boxes]
