from typing import List

from Elements.Element import Element
from Events import PybEvents
from GUIs.GUI import GUI

from Elements.InfoBoxElement import InfoBoxElement


# noinspection PyAttributeOutsideInit
class ERPGUI(GUI):
    """@DynamicAttrs"""

    def initialize(self) -> List[Element]:
        self.info_boxes = []
        ne = InfoBoxElement(self, 372, 125, 50, 15, "PULSES REMAINING", 'BOTTOM', ['0'])
        cp = InfoBoxElement(self, 25, 200, 450, 45, "PARAMETERS", 'BOTTOM', [''])
        ls = InfoBoxElement(self, 25, 300, 450, 45, "LAST PULSE", 'BOTTOM', [''])
        self.info_boxes.append(ne)
        self.info_boxes.append(cp)
        self.info_boxes.append(ls)
        return self.info_boxes

        # def pulses_remaining(self):
        #     if task.started:
        #         return [str(task.npulse * len(task.period) - (task.pulse_count + (task.cur_set - 1) * task.npulse))]
        #     else:
        #         return [str(0)]
        #
        # def cur_params(self):
        #     if task.cur_params is not None:
        #         return str(task.cur_params).split(", 'stages': ")
        #     else:
        #         return ""
        #
        # def last_stim(self):
        #     if task.last_stim is not None:
        #         return str(task.last_stim).split(", 'stages': ")
        #     else:
        #         return ""

    def handle_event(self, event: PybEvents.PybEvent) -> None:
        super(ERPGUI, self).handle_event(event)
        if isinstance(event, PybEvents.TimeoutEvent) and event.name == "erp":
            if self.cur_set <= len(self.period):
                if self.use_sham and self.sham_next:
                    self.sham_next = False
                else:
                    self.pulse_count += 1
                    self.sham_next = True
                if self.pulse_count == self.npulse:
                    self.pulse_count = 0
                    self.cur_set += 1
                self.info_boxes[0].set_text([str(self.npulse * len(self.period) - (self.pulse_count + (self.cur_set - 1) * self.npulse))])
        elif isinstance(event, PybEvents.InfoEvent) and event.name == "SJ_RESPONSE":
            if event.metadata["command"] == "P":
                self.cur_params = event.metadata
                self.info_boxes[1].set_text(str(self.cur_params).split(", 'stages': "))
            elif event.metadata["command"] == "C":
                self.last_stim = event.metadata
                self.info_boxes[2].set_text(str(self.last_stim).split(", 'stages': "))
