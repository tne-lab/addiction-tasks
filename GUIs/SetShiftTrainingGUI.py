from enum import Enum

from Elements.CircleLightElement import CircleLightElement
from Elements.NosePokeElement import NosePokeElement
from Elements.ButtonElement import ButtonElement
from Elements.InfoBoxElement import InfoBoxElement
from Events import PybEvents
from GUIs.GUI import GUI


# noinspection PyAttributeOutsideInit
class SetShiftTrainingGUI(GUI):
    """@DynamicAttrs"""

    class Events(Enum):
        GUI_SHAPE = 0
        GUI_INIT = 1

    def initialize(self):
        self.np_lights = []
        self.np_inputs = []

        for i in range(3):
            npl = CircleLightElement(self, 50 + (i + 1) * (25 + 60), 60, 30, comp=self.nose_poke_lights[i])
            self.np_lights.append(npl)
            npi = NosePokeElement(self, 50 + (i + 1) * (25 + 60), 150, 30, comp=self.nose_pokes[i])
            self.np_inputs.append(npi)

        self.feed_button = ButtonElement(self, 175, 530, 150, 60, "SHAPE", f_size=28)
        self.feed_button.mouse_up = self.shape
        self.init_button = ButtonElement(self, 175, 600, 150, 60, "INITIATE", f_size=28)
        self.init_button.mouse_up = self.init
        self.pellets = InfoBoxElement(self, 200, 440, 100, 30, "PELLETS", 'BOTTOM', ['0'], f_size=28)
        self.time_in_trial = InfoBoxElement(self, 375, 600, 100, 30, "TIME", 'BOTTOM', ['0'], f_size=28)
        self.trial_count = InfoBoxElement(self, 375, 520, 100, 30, "TRIAL", 'BOTTOM', ['1'], f_size=28)

        return [*self.np_lights, *self.np_inputs, self.feed_button, self.init_button, self.pellets, self.time_in_trial, self.trial_count]

    def shape(self, _):
        self.pokes = 0
        self.log_gui_event(self.Events.GUI_SHAPE)
        self.trial_count.set_text(str(self.pokes + 1))

    def init(self, _):
        self.pokes = 0
        self.log_gui_event(self.Events.GUI_INIT)
        self.trial_count.set_text(str(self.pokes + 1))

    def handle_event(self, event: PybEvents.PybEvent) -> None:
        super(SetShiftTrainingGUI, self).handle_event(event)
        self.time_in_trial.set_text(str(round(self.time_elapsed / 60, 2)))
        if isinstance(event, PybEvents.StartEvent):
            self.food.count = 0
            self.pellets.set_text(str(self.food.count))
            self.trial_count.set_text("1")
        elif isinstance(event, PybEvents.ComponentUpdateEvent) and event.comp_id == self.food.id and event.value:
            self.food.count += 1
            self.pellets.set_text(str(self.food.count))
        elif isinstance(event, PybEvents.ComponentUpdateEvent) and (event.comp_id == self.nose_pokes[0].id or event.comp_id == self.nose_pokes[2].id) and event.value:
            if event.comp_id == self.nose_pokes[0].id:
                if (self.nose_poke_lights[0].get_state() and self.training_stage == 'light') or self.training_stage == 'front':
                    self.pokes += 1
                else:
                    self.pokes = 0
            elif event.comp_id == self.nose_pokes[2].id:
                if (self.nose_poke_lights[2].get_state() and self.training_stage == 'light') or self.training_stage == 'rear':
                    self.pokes += 1
                else:
                    self.pokes = 0
            self.trial_count.set_text(str(self.pokes+1))
