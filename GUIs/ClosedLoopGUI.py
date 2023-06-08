from types import MethodType
from typing import List

from Elements.Element import Element
from Elements.FanElement import FanElement
from GUIs import Colors
from GUIs.GUI import GUI

from Elements.InfoBoxElement import InfoBoxElement


class ClosedLoopGUI(GUI):

    def __init__(self, task_gui, task):
        super().__init__(task_gui, task)
        self.info_boxes = []

        def total_pulses(self):
            if task.started:
                return [str(task.pulse_count)]
            else:
                return [str(0)]
                
        #def next_event(self):
        #    if task.started:
        #        return [str(math.ceil(60*task.duration - task.time_in_state()))]
        #    else:
        #        return [str(0)]
                
        tp = InfoBoxElement(self, 100, 125, 50, 15, "Total Pulses", 'BOTTOM', ['0'])
        tp.get_text = MethodType(total_pulses, tp)
        self.info_boxes.append(tp)
        #self.fan = FanElement(self.task_gui, 210, 20, 40, comp=task.fan)
        
        #ne = InfoBoxElement(self, 372, 125, 50, 15, "NEXT EVENT", 'BOTTOM', ['0'])
        #ne.get_text = MethodType(next_event, ne)
        #self.info_boxes.append(ne)

    def get_elements(self) -> List[Element]:
        return [*self.info_boxes]
