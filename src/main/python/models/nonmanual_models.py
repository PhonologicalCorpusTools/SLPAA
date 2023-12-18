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
    def __init__(self, options=None, label=None, exclusive=False):
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
    distance=False,
    action_state=ActionStateModel(options=['Upper teeth touch lower lip',
                                           'Close (bite)',
                                           'Almost close',
                                           'Open',
                                           'Clatter'  # gray out if Static is selected
                                           ])
)
mouth_jaw = NonManualModel(
    label='Jaw (lower jaw)',
    action_state=ActionStateModel(options=[ActionStateModel(label='Horizontal',
                                                            options=['H1 side',
                                                                     'H2 side']),
                                           ActionStateModel(label='Vertical',
                                                            options=['Up',
                                                                     'Down']),
                                           ActionStateModel(label='Sagittal',
                                                            options=['Forward',
                                                                     'Backward'])],
                                  exclusive=False)
)
mouth_opening = NonManualModel(
    label='Mouth opening',
    action_state=ActionStateModel(options=['Yawn',
                                           'Wide open',
                                           'Open',
                                           'Slightly open',
                                           'Closed',
                                           'Tightly closed'
                                           ])
)
mouth_lips = NonManualModel(
    label='lips',
    visibility=False,
    action_state=ActionStateModel(options=[ActionStateModel(label='Openness',
                                                            options=['Wide open',
                                                                     'Open',
                                                                     'Slightly open',
                                                                     'Almost closed',
                                                                     'Closed',
                                                                     'Tightly closed',]),
                                           ActionStateModel(label='Stretch',
                                                            options=['Small stretch',
                                                                     'Large stretch']),
                                           ActionStateModel(label='Raise',
                                                            options=[ActionStateModel(label='upper lip',
                                                                                      options=[
                                                                                          ActionStateModel(label='One side',
                                                                                                           options=['H1 side',
                                                                                                                    'H2 side'],
                                                                                                           exclusive=True),
                                                                                          'Whole',
                                                                                      ],
                                                                                      exclusive=True
                                                                                      ),
                                                                     ActionStateModel(label='corner(s)',
                                                                                      options=[
                                                                                          ActionStateModel(label='One side',
                                                                                                           options=['H1 side',
                                                                                                                    'H2 side'],
                                                                                                           exclusive=True),
                                                                                          'Both sides',
                                                                                      ],
                                                                                      exclusive=True
                                                                                      ),
                                                                     ]
                                                            ),
                                           ActionStateModel(label='Curve down corners',
                                                            options=[ActionStateModel(label='One side',
                                                                                      options=['H1 side',
                                                                                               'H2 side'],
                                                                                      exclusive=True),
                                                                     'Both sides']),
                                           ActionStateModel(label='Pucker'),
                                           ActionStateModel(label='Vibrate'),   # gray out if static
                                           ActionStateModel(label='Purse'),
                                           ActionStateModel(label='Round'),
                                           ActionStateModel(label='Tense'),
                                           ActionStateModel(label='Puff',
                                                            options=['Both lips',
                                                                     ActionStateModel(label='One lip',
                                                                                      options=['Upper lip',
                                                                                               'Lower lip'],
                                                                                      exclusive=True),
                                                                     ],
                                                            ),
                                           ])

)
mouth_tongue = NonManualModel(
    label='tongue',
    action_state=ActionStateModel(options=[ActionStateModel(label='Protrude',
                                                            options=[ActionStateModel(label='Part of tongue',
                                                                                      options=['tip only',
                                                                                               'body of tongue']),
                                                                     ActionStateModel(label='Distance',
                                                                                      options=['past teeth only',
                                                                                               'past teeth and lips']),
                                                                     ActionStateModel(label='Direction',
                                                                                      options=[ActionStateModel(
                                                                                          label='Horizontal',
                                                                                          options=['toward H1',
                                                                                                   'toward H2']),
                                                                                               ActionStateModel(
                                                                                                   label='Vertical',
                                                                                                   options=['up',
                                                                                                            'down']),
                                                                                               ActionStateModel(
                                                                                                   label='Sagittal',
                                                                                                   options=['forward']),
                                                                                               ActionStateModel(
                                                                                                   label='Circular',
                                                                                                   # gray out if static
                                                                                                   options=[])
                                                                                               ],
                                                                                      )]
                                                            ),
                                           ActionStateModel(label='Contact',
                                                            options=[ActionStateModel(label='Behind upper teeth'),
                                                                     ActionStateModel(label='Touch upper lip'),
                                                                     ActionStateModel(label='Touch lower lip'),
                                                                     ActionStateModel(label='Touch lower teeth'),
                                                                     ActionStateModel(label='Touch a corner of the mouth',
                                                                                      options=['H1 side corner',
                                                                                               'H2 side corner']),
                                                                     ActionStateModel(label='Push into cheek',
                                                                                      options=['H1 side cheek',
                                                                                               'H2 side cheek']),
                                                                     ActionStateModel(label='Push behind bottom lip'),
                                                                     ActionStateModel(label='Push behind upper lip')])
                                           ])
)
mouth_cheek = NonManualModel(
    label='cheek',
    action_state=ActionStateModel(options=[ActionStateModel(label='Puff'),
                                           ActionStateModel(label='Such in'),
                                           ],
                                  )

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
                                                                     'H2 side'],
                                                            exclusive=True),
                                           ActionStateModel(label='Move nostril(s)',
                                                            options=['Widen / flare',
                                                                     'Pinch'],
                                                            exclusive=True)])
)


shoulder = NonManualModel(
    label='Shoulder',
    subparts={'specifier': 'side',
              'opposite action': False},
    action_state=ActionStateModel(options=[ActionStateModel(label='Straight',
                                                            options=[ActionStateModel(label='Vertical',
                                                                                      options=['Up', 'Down'],
                                                                                      ),
                                                                     ActionStateModel(label='Sagittal',
                                                                                      options=['Distal', 'Proximal'],
                                                                                      )
                                                                     ],
                                                            exclusive=True),
                                           ActionStateModel(label='Circumduction',
                                                            options=['forward from top of circle',
                                                                     'backward from top of circle'],
                                                            exclusive=True)],
                                   )
)
body = NonManualModel(
    label='Body',
    action_state=ActionStateModel(options=[ActionStateModel(label='Torso',
                                                            options=[ActionStateModel(label='Rotate',
                                                                                      options=['toward H1',
                                                                                               'toward H2']),
                                                                     ActionStateModel(label='Tilt',
                                                                                      options=[ActionStateModel(label='Horizontal',
                                                                                                                options=['toward H1',
                                                                                                                         'toward H2']),
                                                                                               ActionStateModel(label='Sagittal',
                                                                                                                options=['forward',
                                                                                                                         'backward'])
                                                                                               ]
                                                                                      ),]),
                                           ActionStateModel(label='Chest',
                                                            options=['Exhale / deflate',
                                                                     'Inhale / inflate']),
                                           ActionStateModel(label='Back',
                                                            options=['Round', 'Straight']),
                                           ]
                                  )
)
head = NonManualModel(
    label='Head',
    action_state=ActionStateModel(options=[ActionStateModel(label='Rotate',
                                                            options=['toward H1',
                                                                     'toward H2']),
                                           ActionStateModel(label='Tilt',
                                                            options=[ActionStateModel(label='Horizontal',
                                                                                      options=['toward H1',
                                                                                               'toward H2']),
                                                                     ActionStateModel(label='Sagittal',
                                                                                      options=['forward',
                                                                                               'backward'])]),
                                           ActionStateModel(label='Push',
                                                            options=[ActionStateModel(label='Horizontal',
                                                                                      options=['toward H1',
                                                                                               'toward H2']),
                                                                     ActionStateModel(label='Sagittal',
                                                                                      options=['forward',
                                                                                               'backward'])])
                                           ]
                                  )
)

eyegaze = NonManualModel(
    label='Eye gaze',
    subparts={'specifier': 'eye',
              'opposite action': False},
    distance=False,
    action_state=ActionStateModel(options=[ActionStateModel(label='Absolute direction',
                                                            options=[ActionStateModel(label='Horizontal',
                                                                                      options=['Toward H1', 'Toward H2']),
                                                                     ActionStateModel(label='Vertical',
                                                                                      options=['Up', 'Down']),
                                                                     ActionStateModel(label='Sagittal',
                                                                                      options=['Ahead']),
                                                                     ]),
                                           ActionStateModel(label='Relative direction',
                                                            options=['toward Addressee',
                                                                     'toward Researcher',
                                                                     ActionStateModel(label='toward Hands',
                                                                                      options=['Both hands',
                                                                                               ActionStateModel(
                                                                                                   label='One hand',
                                                                                                   options=['H1', 'H2'],
                                                                                                   exclusive=True)
                                                                                               ],
                                                                                      exclusive=True),
                                                                     'toward a discourse reference; specify:',  # specify
                                                                     'toward something else; specify:']),  # specify
                                           'Unfocused',
                                           'Rolling'  # grey out if Static is selected
                                           ])
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
    action_state=ActionStateModel(options=[ActionStateModel(label='Breath',  # grey out if static
                                                            options=['In', 'Out'],
                                                            exclusive=True),
                                           'Hold breath',  # grey out if dynamic
                                           'Press air toward lips'],
                                  )

)

nonmanual_root = NonManualModel(
    children=[shoulder,
              body,
              head,
              eyegaze,
              facexp,
              mouth,
              air
              ]
)
