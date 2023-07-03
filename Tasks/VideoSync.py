from enum import Enum

from Events import PybEvents
from Tasks.Task import Task
from Components.Video import Video


class VideoSync(Task):
    """@DynamicAttrs"""

    class States(Enum):
        RECORDING = 0

    @staticmethod
    def get_components():
        return {
            'cam': [Video]
        }

    # noinspection PyMethodMayBeStatic
    def get_constants(self):
        return {
            'duration': None
        }

    def init_state(self):
        return self.States.RECORDING

    def start(self):
        self.cam.start()
        if self.duration is not None:
            self.set_timeout("complete", self.duration * 60)

    def stop(self):
        self.cam.stop()

    def all_states(self, event: PybEvents.PybEvent) -> bool:
        if isinstance(event, PybEvents.TimeoutEvent) and event.name == "complete":
            self.complete = True
            return True
        return False
