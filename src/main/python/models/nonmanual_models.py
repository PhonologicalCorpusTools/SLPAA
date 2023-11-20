class NonManualModel:
    def __init__(self, label='root', children=None, subparts=None, visibility=None, distance=None, action_state=None):
        self.label = label        # label to be shown in tab gui
        self.children = children  # relevant for nested tabs. e.g., facial expression and mouth
        self.subparts = subparts

        self.static = 'static'    # static or dynamic
        self.neutral = True
        self.visibility = visibility  # Bool. visibility is only relevant for 'teeth' and 'lips'
        self.action_state = action_state
        self.mvmt_char = None       # movement characteristics
        self.distance = distance    # distance is only relevant for 'eye gaze' and 'teeth'



# daughters of major non-manual module 'Mouth'
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

# daughters of major non-manual module 'Facial Expression'
facial_eyebrows = NonManualModel(
    label='Eyebrows',
    subparts={'specifier': 'side',
              'opposite action': True},
)
facial_eyelids = NonManualModel(
    label='Eyelids',
    subparts={'specifier': 'side',
              'opposite action': False},
)
facial_nose = NonManualModel(
    label='Nose',
)


shoulder = NonManualModel(
    label='Shoulder',
    subparts={'specifier': 'side',
              'opposite action': False},
    action_state={
        'Straight': [{'Vertical': ['Up', 'Down'],
                     'Sagittal': ['Distal', 'Proximal']}],
        'Circumduction': ['forward from top of circle',
                          'backward from top of circle']

    }
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
