# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventDestroyTimersPanelMeta.py
from gui.Scaleform.daapi.view.battle.shared.destroy_timers_panel import DestroyTimersPanel

class EventDestroyTimersPanelMeta(DestroyTimersPanel):

    def as_setWarningTextS(self, text, vis):
        return self.flashObject.as_setWarningText(text, vis) if self._isDAAPIInited() else None
