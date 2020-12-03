
class MetaData:
    def __init__(self, coder, update_date, note):
        self._coder = coder
        self._update_date = update_date
        self._note = note

    @property
    def coder(self):
        return self._coder

    @coder.setter
    def coder(self, new_coder):
        self._coder = new_coder

    @property
    def update_date(self):
        return self._update_date

    @update_date.setter
    def update_date(self, new_update_date):
        self._update_date = new_update_date

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, new_note):
        self._note = new_note


class GlobalHandshapeOption:
    def __init__(self, is_estimated, is_uncertain, is_incomplete):
        self._estimated = is_estimated
        self._uncertain = is_uncertain
        self._incomplete = is_incomplete

    @property
    def estimated(self):
        return self._estimated

    @estimated.setter
    def estimated(self, new_is_estimated):
        self._estimated = new_is_estimated

    @property
    def uncertain(self):
        return self._uncertain

    @uncertain.setter
    def uncertain(self, new_is_uncertain):
        self._uncertain = new_is_uncertain

    @property
    def incomplete(self):
        return self._incomplete

    @incomplete.setter
    def incomplete(self, new_is_incomplete):
        self._incomplete = new_is_incomplete

class QualityParameter:
    def __init__(self, contact='none', non_temporal='none', temporal='none'):
        self._contact = contact
        self._non_temporal = non_temporal
        self._temporal = temporal

class Parameter:
    def __init__(self, quality_parameter):
        self._quality_parameter = quality_parameter

class Sign:
    def __init__(self, gloss, freq):
        self._gloss = gloss
        self._freq = freq
