from types import MethodType
from typing import List

from Elements.Element import Element
from GUIs.GUI import GUI

from Elements.InfoBoxElement import InfoBoxElement


class ERPGUI(GUI):

    def __init__(self, task_gui, task):
        super().__init__(task_gui, task)
        self.info_boxes = []

        def pulses_remaining(self):
            if task.started:
                return [str(task.npulse * len(task.period) - (task.pulse_count + (task.cur_set - 1) * task.npulse))]
            else:
                return [str(0)]

        def cur_params(self):
            if task.cur_params is not None:
                return str(task.cur_params).split(", 'stages': ")
            else:
                return ""

        def last_stim(self):
            if task.last_stim is not None:
                return str(task.last_stim).split(", 'stages': ")
            else:
                return ""

        ne = InfoBoxElement(self, 372, 125, 50, 15, "PULSES REMAINING", 'BOTTOM', ['0'])
        ne.get_text = MethodType(pulses_remaining, ne)
        cp = InfoBoxElement(self, 25, 200, 450, 45, "PARAMETERS", 'BOTTOM', [''])
        cp.get_text = MethodType(cur_params, cp)
        ls = InfoBoxElement(self, 25, 300, 450, 45, "LAST PULSE", 'BOTTOM', [''])
        ls.get_text = MethodType(last_stim, ls)
        self.info_boxes.append(ne)
        self.info_boxes.append(cp)
        self.info_boxes.append(ls)

    def get_elements(self) -> List[Element]:
        return [*self.info_boxes]
