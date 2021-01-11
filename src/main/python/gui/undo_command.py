#from PyQt5.QtCore import ()
from PyQt5.QtWidgets import (
    QUndoCommand
)
#from PyQt5.QtGui import ()


class TranscriptionUndoCommand(QUndoCommand):
    def __init__(self, slot, old_prop, new_prop, **kwargs):
        super().__init__(**kwargs)

        self.slot = slot
        self.old_prop = old_prop
        self.new_prop = new_prop

    def redo(self):
        self.slot.set_value_from_dict(self.new_prop)

    def undo(self):
        self.slot.set_value_from_dict(self.old_prop)
