import os
import json
from PyQt5 import QtCore


settings_file   = os.path.join('settings', 'data.db')

class VentModel(QtCore.QAbstractListModel):
    def __init__(self, *args, settings=None, **kwargs):
        super(VentModel, self).__init__(*args, **kwargs)
        self.settings = settings or []

    def load(self):
        try:
            with open(settings_file, 'r') as f:
                self.settings = json.load(f)
        except Exception:
            pass

    def save(self):
        with open(settings_file, 'w') as f:
            data = json.dump(self.settings, f)