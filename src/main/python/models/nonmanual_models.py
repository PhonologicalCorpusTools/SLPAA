class NonManualModel:
    def __init__(self, label='root', children=None, subparts=None, visibility=None, distance=None, action_state=None):
        self.label = label        # label to be shown in tab gui
        self.children = children  # relevant for nested tabs. e.g., facial expression and mouth
        self.subparts = subparts

        # properties
        self._static = True    # Bool. True = static / False = dynamic.
        self._neutral = False
        self._visibility = visibility  # Bool. visibility is only relevant for 'teeth' and 'lips'
        self._action_state = action_state
        self._mvmt_char = None       # movement characteristics
        self._distance = distance    # distance is only relevant for 'eye gaze' and 'teeth'

    @property
    def static(self):
        return self._static

    @static.setter
    def static(self, value):
        if not isinstance(value, bool):
            raise ValueError("'static' value must be a boolean")
        self._static = value

    @property
    def neutral(self):
        return self._neutral

    @neutral.setter
    def neutral(self, value):
        if not isinstance(value, bool):
            raise ValueError("'neutral' value must be a boolean")
        self._neutral = value

    @property
    def visibility(self):
        return self._visibility

    @visibility.setter
    def visibility(self, value):
        if not isinstance(value, bool):
            raise ValueError("'visibility' value must be a boolean")
        self._visibility = value

    @property
    def action_state(self):
        return self._action_state

    @action_state.setter
    def action_state(self, value):
        self._action_state = value

    @property
    def mvmt_char(self):
        return self._mvmt_char

    @mvmt_char.setter
    def mvmt_char(self, value):
        self._mvmt_char = value

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, value):
        if not isinstance(value, bool):
            raise ValueError("'static' value must be a boolean")
        self._distance = value


class ActionStateModel:
    def __init__(self, options, label=None, exclusive=False):
        self.label = label
        self.exclusive = exclusive
        self.options = options

        self._value = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value



# children of major non-manual module 'Mouth'
mouth_teeth = NonManualModel(
    label='Teeth',
    visibility=False,
    distance=False
)
mouth_jaw = NonManualModel(
    label='Jaw (lower jaw)'
)
mouth_opening = NonManualModel(
    label='Mouth opening'
)
mouth_lips = NonManualModel(
    label='lips',
    visibility=False
)
mouth_tongue = NonManualModel(
    label='tongue'
)
mouth_cheek = NonManualModel(
    label='cheek'
)

# children of major non-manual module 'Facial Expression'
facial_eyebrows = NonManualModel(
    label='Eyebrows',
    subparts={'specifier': 'side',
              'opposite action': True},
    action_state=ActionStateModel(options=['Furrow', #  [gray out if ‘one side’ is checked]
                                           'Up',
                                           'Down',
                                           ])
)
facial_eyelids = NonManualModel(
    label='Eyelids',
    subparts={'specifier': 'side',
              'opposite action': False},
    action_state=ActionStateModel(options=['Wide open', #  [gray out if ‘one side’ is checked]
                                           'Open',
                                           'Narrow',
                                           'Close',
                                           'Tightly shut',
                                           ])
)
facial_nose = NonManualModel(
    label='Nose',
    action_state=ActionStateModel(options=['Wrinkle',
                                           ActionStateModel(label='Move to side',
                                                            options=['H1 side',
                                                                     'H2 side']),
                                           ActionStateModel(label='Move nostril(s)',
                                                            options=['Widen / flare',
                                                                     'Pinch'])])
)


shoulder = NonManualModel(
    label='Shoulder',
    subparts={'specifier': 'side',
              'opposite action': False},
    action_state=ActionStateModel(options=[ActionStateModel(label='Straight',
                                                             options=[ActionStateModel(label='Vertical',
                                                                                       options=['Up', 'Down'],
                                                                                       exclusive=True),
                                                                      ActionStateModel(label='Sagittal',
                                                                                       options=['Distal','Proximal'],
                                                                                       exclusive=True)],
                                                             exclusive=True),
                                            ActionStateModel(label='Circumduction',
                                                             options=['forward from top of circle',
                                                                      'backward from top of circle'],
                                                             exclusive=True)],
                                   )
)
body = NonManualModel(
    label='Body',
)
head = NonManualModel(
    label='Head',
)
eyegaze = NonManualModel(
    label='Eye gaze',
    subparts={'specifier': 'eye',
              'opposite action': False},
    distance=False
)
facexp = NonManualModel(
    label='Facial Expression',
    children=[facial_eyebrows,
              facial_eyelids,
              facial_nose]
)
mouth = NonManualModel(
    label='Mouth',
    children=[mouth_teeth,
              mouth_jaw,
              mouth_opening,
              mouth_lips,
              mouth_tongue,
              mouth_cheek]
)
air = NonManualModel(
    label='Air',
)

nonmanual_root = NonManualModel(
    children=[shoulder, body, head, eyegaze, facexp, mouth, air]
)
