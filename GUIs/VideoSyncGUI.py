from types import MethodType
from typing import List

from Elements.Element import Element
from Elements.InfoBoxElement import InfoBoxElement
from GUIs.GUI import GUI


class VideoSyncGUI(GUI):

    def __init__(self, task_gui, task):
        super().__init__(task_gui, task)

        def time_left_text(_):
            if task.duration is not None:
                return [str(round(task.duration - task.time_elapsed() / 60, 2))]
            else:
                return ["None"]

        self.time_left = InfoBoxElement(self, 200, 440, 100, 30, "TIME REMAINING", 'BOTTOM', ['0'], f_size=28)
        self.time_left.get_text = MethodType(time_left_text, self.time_left)

    def get_elements(self) -> List[Element]:
        return [self.time_left]
