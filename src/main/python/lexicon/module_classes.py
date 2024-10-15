from datetime import datetime
from fractions import Fraction
from itertools import chain
import logging

from PyQt5.QtCore import (
    Qt,
    QSettings
)

from constant import NULL, PREDEFINED_MAP, HAND, ARM, LEG
PREDEFINED_MAP = {handshape.canonical: handshape for handshape in PREDEFINED_MAP.values()}

treepathdelimiter = ">"  # TODO KV - should this be user-defined in global settings? or maybe even in the module window(s)?


class ModuleTypes:
    MOVEMENT = 'movement'
    LOCATION = 'location'
    HANDCONFIG = 'handconfig'
    RELATION = 'relation'
    ORIENTATION = 'orientation'
    NONMANUAL = 'nonmanual'

    abbreviations = {
        MOVEMENT: 'Mov',
        LOCATION: 'Loc',
        HANDCONFIG: 'Config',
        RELATION: 'Rel',
        ORIENTATION: 'Ori',
        NONMANUAL: 'NonMan'
    }


class UserDefinedRoles(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


userdefinedroles = UserDefinedRoles({
    'selectedrole': 0,
        # selectedrole:
        # Used by MovementTreeItem, LocationTreeItem, MovementListItem, LocationListItem to indicate
        # whether they are selected by the user. Not exactly the same as ...Item.checkState() because:
        #   (1) selectedrole only uses True & False whereas checkstate has none/partial/full, and
        #   (2) ListItems don't actually get checked, but we still need to track whether they've been selected
    'pathdisplayrole': 1,
        # pathdisplayrole:
        # Used by LocationTreeModel, LocationListModel, LocationPathsProxyModel (and similar for Movement) to access
        # the full path (node names, separated by delimiters) of the model Item in question,
        # generally for purposes of displaying in the selectd paths list in the Location or Movement dialog
    'mutuallyexclusiverole': 2,
        # mutuallyexclusiverole:
        # Used by MovementTreeItem & LocationTreeItem to identify the item's relationship to its siblings,
        # which also involves its display as a radio button vs a checkbox.
    'nocontrolrole': 3,
        # nocontrolrole:
        # used by MovementTreeItemDelegate when a MovementTreeItem is never a selectable item
        # so text may be displayed, but no checkbox or radiobutton
    'firstingrouprole': 4,
        # firstingrouprole:
        # used by MovementTreeItemDelegate to determine whether the relevant model Item is the first
        # in its subgroup, which affects how it is painted in the movement tree
        # (eg, whether the item will be preceded by a horizontal line)
    'firstsubgrouprole': 5,
        # firstsubgrouprole:
        # Used by MovementTreeItem & LocationTreeItem to identify whether an item that is in a subgroup is
        # also in the *first* subgroup in its section. Such a subgroup will not have a horizontal line drawn before it.
    'subgroupnamerole': 6,
        # subgroupnamerole:
        # Used by MovementTreeItem & LocationTreeItem to identify which items are grouped together. Such
        # subgroups are separated from other siblings by a horizontal line in the tree, and item selection
        # is often (always?) mutually exclusive within the subgroup.
    'nodedisplayrole': 7,
        # nodedisplayrole:
        # Used by MovementListItem & LocationListItem to store just the corresponding treeitem's node name
        # (not the entire path), currently only for sorting listitems by alpha (by lowest node).
    'timestamprole': 8,
        # timestamprole:
        # Used by LocationPathsProxyModel and MovementPathsProxyModel as one option on which to sort selected paths
    'isuserspecifiablerole': 9,
        # isuserspecifiablerole:
        # Used by MovementTreeItem to indicate that this tree item allows the user to specify a particular value.
        # If 0, the corresponding QStandardItem (ie, the "editable part") is marked not editable; the user cannot change its value;
        # If 1, the corresponding QStandardItem is marked editable but must be a number, >= 1, and a multiple of 0.5;
        # If 2, the corrresponding QStandardItem is marked editable but must be a number;
        # If 3, the corrresponding QStandardItem is marked editable with no restrictions.
        # This kind of editable functionality was formerly achieved via a separate (subsidiary) editable MovementTreeItem.
    'userspecifiedvaluerole': 10,
        # userspecifiedvaluerole:
        # Used by MovementTreeItem to store the (string) value for an item that is allowed to be user-specified.

})


# TODO KV comments
# TODO KV - for parameter modules and x-slots
# common ancestor for (eg) HandshapeModule, MovementModule, etc
class ParameterModule:

    def __init__(self, articulators, timingintervals=None, phonlocs=None, addedinfo=None):
        self._articulators = articulators
        self._phonlocs = phonlocs
        self._timingintervals = []
        if timingintervals is not None:
            self.timingintervals = timingintervals
        self._addedinfo = addedinfo if addedinfo is not None else AddedInfo()
        self._uniqueid = datetime.timestamp(datetime.now())

    @property
    def addedinfo(self):
        return self._addedinfo

    @addedinfo.setter
    def addedinfo(self, addedinfo):
        self._addedinfo = addedinfo

    @property
    def articulators(self):
        if not hasattr(self, '_articulators'):
            # backward compatibility pre-20230804 addition of arms and legs as articulators (issues #175 and #176)
            articulator_dict = {1: False, 2: False}
            if hasattr(self, '_hands'):
                articulator_dict[1] = self._hands['H1']
                articulator_dict[2] = self._hands['H2']
            self._articulators = (HAND, articulator_dict)
        return self._articulators

    @articulators.setter
    def articulators(self, articulators):
        self._articulators = articulators
    
    @property
    def phonlocs(self):
        if not hasattr(self, '_phonlocs'):
            self.phonlocs = PhonLocations()
        return self._phonlocs 

    @phonlocs.setter
    def phonlocs(self, phonlocs):
        self._phonlocs = phonlocs

    @property
    def uniqueid(self):
        return self._uniqueid

    @uniqueid.setter
    def uniqueid(self, uniqueid):
        self._uniqueid = uniqueid

    @property
    def timingintervals(self):
        return self._timingintervals

    @timingintervals.setter
    def timingintervals(self, timingintervals):
        self._timingintervals = [t for t in timingintervals]

    def getabbreviation(self):
        return "Module abbreviations not yet implemented"


class EntryID:
    nodisplay = "[No selected Entry ID elements to display]"

    def __init__(self, counter=None, parentsign=None):
        self.parentsign = parentsign
        # all other attributes of EntryID are sourced from QSettings, sign, and/or sign-level info,
        # so that they're not stored twice (and therefore we don't need to update in multiple places
        # if any of those values change)
        self._counter = counter

        # TODO - eventually add other attributes (coder, signer, source, recording info)
        # see class EntryIDTab in preference_dialog.py
        # and https://github.com/PhonologicalCorpusTools/SLPAA/issues/18#issuecomment-1074184453

    @property
    def counter(self):
        return self._counter

    @counter.setter
    def counter(self, new_counter):
        self._counter = new_counter

    @property
    def date(self):
        if self.parentsign is not None:
            return self.parentsign.signlevel_information.datecreated
        else:  # this shouldn't ever actually happen, but just in case...
            return datetime.now()

    def getattributestringfromname(self, attr_name, qsettings):
        if attr_name == 'date':
            return "" if self.date is None else self.date.strftime(qsettings.value('entryid/date/format', type=str))
        elif attr_name == 'counter':
            counter_string = str(self.counter)
            return "0" * (qsettings.value('entryid/counter/digits', type=int) - len(counter_string)) + counter_string
        elif attr_name in dir(self):
            # assuming we have a @property function for this attribute and it doesn't need any additional formatting
            return getattr(self, attr_name)
        else:
            return ""

    def display_string(self):
        
        if self.counter in [None, ""]:
            return ""
        qsettings = QSettings()  # organization name & application name were set in MainWindow.__init__()

        orders_strings = []
        for attr in ['counter', 'date']:  # could these come from 'attr in dir(self)' instead?
            if qsettings.value('entryid/' + attr + '/visible', type=bool):
                orders_strings.append((qsettings.value('entryid/' + attr + '/order', type=int), self.getattributestringfromname(attr, qsettings)))
        orders_strings.sort()
        return qsettings.value('entryid/delimiter', type=str).join([string for (order, string) in orders_strings]) or self.nodisplay

    # == check compares the displayed strings
    def __eq__(self, other):
        if isinstance(other, EntryID):
            return self.display_string() == other.display_string()
        return False

    # != check compares the displayed strings
    def __ne__(self, other):
        return not self.__eq__(other)

    # < check compares the displayed strings
    def __lt__(self, other):
        if isinstance(other, EntryID):
            return self.display_string() < other.display_string()
        return False

    # > check compares the displayed strings
    def __gt__(self, other):
        return other.__lt__(self)

    # <= check compares the displayed strings
    def __le__(self, other):
        return not self.__gt__(other)

    # >= check compares the displayed strings
    def __ge__(self, other):
        return not self.__lt__(other)

    def __repr__(self):
        return repr(self.display_string())


class SignLevelInformation:
    def __init__(self, signlevel_info=None, serializedsignlevelinfo=None, parentsign=None):
        self._parentsign = parentsign

        if serializedsignlevelinfo is not None:
            datecreated = datetime.fromtimestamp(serializedsignlevelinfo['date created'])
            # as of 20240209, entryid has shifted from being an integer to an EntryID object
            # but due to complications with EntryID containing a reference to its parent Sign,
            # we still store it as only the counter value and then recreate when loading from file
            self._entryid = EntryID(counter=serializedsignlevelinfo['entryid'], parentsign=self.parentsign)
            # as of 20231208, gloss is now a list rather than a string
            self._gloss = [serializedsignlevelinfo['gloss']] if isinstance(serializedsignlevelinfo['gloss'], str) else serializedsignlevelinfo['gloss']
            self._lemma = serializedsignlevelinfo['lemma']
            # backward compatibility for attribute added 20231211
            self._idgloss = serializedsignlevelinfo['idgloss'] if 'idgloss' in serializedsignlevelinfo.keys() else ''
            self._source = serializedsignlevelinfo['source']
            self._signer = serializedsignlevelinfo['signer']
            self._frequency = serializedsignlevelinfo['frequency']
            self._coder = serializedsignlevelinfo['coder']
            self._datecreated = datecreated
            self._datelastmodified = datetime.fromtimestamp(serializedsignlevelinfo['date last modified'])
            self._note = serializedsignlevelinfo['note']
            # backward compatibility for attribute added 20230412
            self._fingerspelled = 'fingerspelled' in serializedsignlevelinfo.keys() and serializedsignlevelinfo['fingerspelled']
            self._compoundsign = 'compoundsign' in serializedsignlevelinfo.keys() and serializedsignlevelinfo['compoundsign']
            self._handdominance = serializedsignlevelinfo['handdominance']
        elif signlevel_info is not None:
            self._entryid = EntryID(counter=signlevel_info['entryid'], parentsign=parentsign)
            self._gloss = signlevel_info['gloss']
            self._lemma = signlevel_info['lemma']
            self._idgloss = signlevel_info['idgloss']
            self._source = signlevel_info['source']
            self._signer = signlevel_info['signer']
            self._frequency = signlevel_info['frequency']
            self._coder = signlevel_info['coder']
            self._datecreated = signlevel_info['date created']
            self._datelastmodified = signlevel_info['date last modified']
            self._note = signlevel_info['note']
            # backward compatibility for attribute added 20230412!
            self._fingerspelled = 'fingerspelled' in signlevel_info.keys() and signlevel_info['fingerspelled']
            self._compoundsign = 'compoundsign' in signlevel_info.keys() and signlevel_info['compoundsign']
            self._handdominance = signlevel_info['handdominance']

    def __eq__(self, other):
        if isinstance(other, SignLevelInformation):
            self_attributes = self.__dict__
            other_attributes = other.__dict__
            return False not in [self_attributes[attr] == other_attributes[attr] for attr in self_attributes.keys()]
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def serialize(self):
        return {
            'entryid': self._entryid.counter,
            'gloss': self._gloss,
            'lemma': self._lemma,
            'idgloss': self._idgloss,
            'source': self._source,
            'signer': self._signer,
            'frequency': self._frequency,
            'coder': self._coder,
            'date created': self._datecreated.timestamp(),
            'date last modified': self._datelastmodified.timestamp(),
            'note': self._note,
            'fingerspelled': self._fingerspelled,
            'compoundsign': self._compoundsign,
            'handdominance': self._handdominance
        }

    @property
    def parentsign(self):
        return self._parentsign

    @parentsign.setter
    def parentsign(self, new_parentsign):
        self._parentsign = new_parentsign
        self._entryid.parentsign = new_parentsign

    @property
    def entryid(self):
        return self._entryid

    @entryid.setter
    def entryid(self, new_entryid):
        if new_entryid.parentsign is None:
            new_entryid.parentsign = self.parentsign
        self._entryid = new_entryid

    @property
    def gloss(self):
        return self._gloss

    @gloss.setter
    def gloss(self, new_gloss):
        self._gloss = new_gloss

    @property
    def lemma(self):
        return self._lemma

    @lemma.setter
    def lemma(self, new_lemma):
        self._lemma = new_lemma

    @property
    def idgloss(self):
        if not hasattr(self, '_idgloss'):
            self._idgloss = ''
        return self._idgloss

    @idgloss.setter
    def idgloss(self, new_idgloss):
        self._idgloss = new_idgloss

    @property
    def fingerspelled(self):
        if not hasattr(self, '_fingerspelled'):
            # backward compatibility for attribute added 20230412!
            self._fingerspelled = False  # default value
        return self._fingerspelled

    @fingerspelled.setter
    def fingerspelled(self, new_fingerspelled):
        self._fingerspelled = new_fingerspelled

    @property
    def compoundsign(self):
        if not hasattr(self, '_compoundsign'):
            # backward compatibility for attribute added 20230503!
            self._compoundsign = False  # default value
        return self._compoundsign
    
    @compoundsign.setter
    def compoundsign(self, new_compoundsign):
        self._compoundsign = new_compoundsign

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, new_source):
        self._source = new_source

    @property
    def signer(self):
        return self._signer

    @signer.setter
    def signer(self, new_signer):
        self._signer = new_signer

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, new_frequency):
        self._frequency = new_frequency

    @property
    def coder(self):
        return self._coder

    @coder.setter
    def coder(self, new_coder):
        self._coder = new_coder

    @property
    def datecreated(self):
        return self._datecreated

    # input should be a datetime object
    @datecreated.setter
    def datecreated(self, new_datecreated):
        self._datecreated = new_datecreated

    @property
    def datelastmodified(self):
        return self._datelastmodified

    # input should be a datetime object
    @datelastmodified.setter
    def datelastmodified(self, new_datelastmodified):
        self._datelastmodified = new_datelastmodified

    def lastmodifiednow(self):
        self._datelastmodified = datetime.now()

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, new_note):
        self._note = new_note

    @property
    def handdominance(self):
        return self._handdominance

    @handdominance.setter
    def handdominance(self, new_handdominance):
        self._handdominance = new_handdominance


# This module stores the movement information for a particular articulator/s.
# It also stores "Added Info" (estimated, uncertain, etc) characteristics for each selected movement
# as well as for the module overall.
class MovementModule(ParameterModule):
    def __init__(self, movementtreemodel, articulators, timingintervals=None, phonlocs=None, addedinfo=None, inphase=0):
        self._movementtreemodel = movementtreemodel
        self._inphase = inphase    # TODO KV is "inphase" actually the best name for this attribute?
        super().__init__(articulators, timingintervals=timingintervals, phonlocs=phonlocs, addedinfo=addedinfo)

    @property
    def movementtreemodel(self):
        return self._movementtreemodel

    @movementtreemodel.setter
    def movementtreemodel(self, movementtreemodel):
        self._movementtreemodel = movementtreemodel

    @property
    def inphase(self):
        return self._inphase

    @inphase.setter
    def inphase(self, inphase):
        self._inphase = inphase

    def getabbreviation(self):
        
        wordlist = []

        udr = userdefinedroles
        listmodel = self._movementtreemodel.listmodel
        abbrevs = {
            "Perceptual shape": "Perceptual",
            "Straight": "Straight",
            # "Interacts with subsequent straight movement": "interacts with subseq. straight mov.",
            "Movement contours cross (e.g. X)": "crosses subseq. mov.",
            "Subsequent movement starts at end of first (e.g. ↘↗)": "ends where subseq. mov starts",
            "Subsequent movement starts in same location as start of first (e.g. ↖↗)": "starts where subseq. mov starts",
            "Subsequent movement ends in same location as end of first (e.g. ↘↙)": "ends where subseq. mov. ends",
            "Arc": "Arc",
            "Circle": "Circle",
            "Zigzag": "Zigzag",
            "Loop (travelling circles)": "Loop",
            "Joint-specific movements": "Joint-specific",
            "Nodding/un-nodding": "Nod/Un-",
            "Nodding": "nod",
            "Un-nodding": "un-nod",
            "Pivoting": "Pivot",
            "Radial": "radial pivot",
            "Ulnar": "ulnar pivot",
            "Twisting": "Twist",
            "Pronation": "pronation",
            "Supination": "supination",
            "Closing/Opening": "Close/Open",
            "Closing": "close",
            "Opening": "open",
            "Pinching/unpinching": "Pinch/Un-",
            "Pinching (Morgan 2017)": "pinch",
            "Unpinching": "unpinch",
            "Flattening/Straightening": "Flatten/Straighten",
            "Flattening/hinging": "flatten",
            "Straightening": "straighten",
            "Hooking/Unhooking": "Hook/Un-",
            "Hooking/clawing": "hook",
            "Unhooking": "unhook",
            "Spreading/Unspreading": "Spread/Un-",
            "Spreading": "spread",
            "Unspreading": "unspread",
            "Rubbing": "Rub",
            "Wiggling/Fluttering": "Wiggle",
            "Up": "up",
            "Down": "down",
            "Distal": "dist",
            "Proximal": "prox",
            "Ipsilateral": "ipsi",
            "Contralateral": "contra",
            "Right": "right",
            "Left": "left",
            "Mid-sagittal": "mid-sag",
            "Clockwise": "clockwise",
            "Counterclockwise": "counter-clockwise",
            "Horizontal": "Hor",
            "Vertical": "Ver",
            "Single": "1x",
            "2": "2x",
            "3": "3x",
            "4": "4x",  # TODO automate the abbreviations for integers
            ""
            "Same location": "same loc",
            "Different location": "diff. loc",
            "Trilled": "Trilled",
            "Bidirectional": "Bidirec"
        }
        # 
        numrows = listmodel.rowCount()
        for rownum in range(numrows):
            item = listmodel.item(rownum)
            text = item.text()
            id = item.nodeID
            # logging.warn(rownum)
            # logging.warn(item)
            # logging.warn(id)
            selected = item.data(Qt.UserRole+udr.selectedrole)
            if selected:
                # logging.warn(text)
                # logging.warn(id)
                pathelements = text.split(treepathdelimiter)
                # thisentrytext = ""
                # firstonedone = False
                # morethanone = False
                for pathelement in pathelements:
                    if pathelement in abbrevs.keys():  #  and abbrevs[pathelement] not in thisentrytext:
                        wordlist.append(abbrevs[pathelement])
                #         if not firstonedone:
                #             thisentrytext += abbrevs[pathelement]
                #             firstonedone = True
                #         else:
                #             if not morethanone:
                #                 thisentrytext += " (" + abbrevs[pathelement] + ", "
                #                 morethanone = True
                #     if morethanone:  # and thisentrytext.endswith(")"):
                #         thisentrytext += ")"  # = thisentrytext[:-2] + ")"
                # wordlist.append(thisentrytext)

        return "; ".join(wordlist)


# this class stores info about whether an instance of the Location module represents a phonetic/phonological location
class PhonLocations:

    def __init__(self, phonologicalloc=False, majorphonloc=False, minorphonloc=False, phoneticloc=False):
        self._phonologicalloc = phonologicalloc
        self._majorphonloc = majorphonloc
        self._minorphonloc = minorphonloc
        self._phoneticloc = phoneticloc

    def __eq__(self, other):
        if isinstance(other, PhonLocations):
            self_attributes = self.__dict__
            other_attributes = other.__dict__
            return False not in [self_attributes[attr] == other_attributes[attr] for attr in self_attributes.keys()]
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def phonologicalloc(self):
        return self._phonologicalloc

    @phonologicalloc.setter
    def phonologicalloc(self, phonologicalloc):
        self._phonologicalloc = phonologicalloc

    @property
    def majorphonloc(self):
        return self._majorphonloc

    @majorphonloc.setter
    def majorphonloc(self, majorphonloc):
        self._majorphonloc = majorphonloc

    @property
    def minorphonloc(self):
        return self._minorphonloc

    @minorphonloc.setter
    def minorphonloc(self, minorphonloc):
        self._minorphonloc = minorphonloc

    @property
    def phoneticloc(self):
        return self._phoneticloc

    @phoneticloc.setter
    def phoneticloc(self, phoneticloc):
        self._phoneticloc = phoneticloc

    def allfalse(self):
        return not (self._phoneticloc or self._phonologicalloc or self._majorphonloc or self._minorphonloc)


# this class stores info about what kind of location type (body or signing space)
# is used by a particular instance of the Location Module
class LocationType:

    def __init__(self, body=False, signingspace=False, bodyanchored=False, purelyspatial=False):
        self._body = body
        self._signingspace = signingspace
        self._bodyanchored = bodyanchored
        self._purelyspatial = purelyspatial

    def __repr__(self):
        repr_str = "nil"
        if self._body:
            repr_str = "body"
        elif self._signingspace:
            repr_str = "signing space"
            if self._bodyanchored:
                repr_str += " (body anchored)"
            elif self._purelyspatial:
                repr_str += " (purely spatial)"

        return '<LocationType: ' + repr(repr_str) + '>'

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, checked):
        self._body = checked

        if checked:
            self._signingspace = False
            self._bodyanchored = False
            self._purelyspatial = False

    @property
    def signingspace(self):
        return self._signingspace

    @signingspace.setter
    def signingspace(self, checked):
        self._signingspace = checked

        if checked:
            self._body = False

    @property
    def bodyanchored(self):
        return self._bodyanchored

    @bodyanchored.setter
    def bodyanchored(self, checked):
        self._bodyanchored = checked

        if checked:
            self._signingspace = True

            self._purelyspatial = False
            self._body = False

    @property
    def purelyspatial(self):
        return self._purelyspatial

    @purelyspatial.setter
    def purelyspatial(self, checked):
        self._purelyspatial = checked

        if checked:
            self._signingspace = True

            self._bodyanchored = False
            self._body = False


    def usesbodylocations(self):
        return self._body or self._bodyanchored

    def allfalse(self):
        return not (self._body or self._signingspace or self._bodyanchored or self._purelyspatial)

    def locationoptions_changed(self, previous):
        changed = self.usesbodylocations() and previous.purelyspatial
        changed = changed or (self.purelyspatial and previous.usesbodylocations())
        changed = changed or (previous.usesbodylocations() or previous.purelyspatial)
        changed = changed or (previous.allfalse() and not self.allfalse())
        return changed


# TODO KV comments
# TODO KV - for parameter modules and x-slots
class TimingPoint:

    def __init__(self, wholepart, fractionalpart):
        self._wholepart = wholepart
        self._fractionalpart = fractionalpart

    def __repr__(self):
        return '<TimingPoint: ' + repr(self._wholepart) + ', ' + repr(self._fractionalpart) + '>'

    @property
    def wholepart(self):
        return self._wholepart

    @wholepart.setter
    def wholepart(self, wholepart):
        self._wholepart = wholepart

    @property
    def fractionalpart(self):
        return self._fractionalpart

    @fractionalpart.setter
    def fractionalpart(self, fractionalpart):
        self._fractionalpart = fractionalpart

    def __eq__(self, other):
        if isinstance(other, TimingPoint):
            if self._wholepart == other.wholepart and self._fractionalpart == other.fractionalpart:
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    # do not implement this, because TimingPoint objects are mutable
    # def __hash__(self):
    #     pass

    def __lt__(self, other):
        if isinstance(other, TimingPoint):
            if self._wholepart < other.wholepart:
                return True
            elif self._wholepart == other.wholepart:
                if self._fractionalpart < other.fractionalpart:
                    return True
        return False

    def equivalent(self, other):
        if isinstance(other, TimingPoint):
            return self.adjacent(other) or self.__eq__(other)

    def adjacent(self, other):
        if isinstance(other, TimingPoint):
            if self.fractionalpart == 1 and other.fractionalpart == 0 and (self.wholepart + 1 == other.wholepart):
                return True
            elif other.fractionalpart == 1 and self.fractionalpart == 0 and (other.wholepart + 1 == self.wholepart):
                return True
            else:
                return False

    def __gt__(self, other):
        if isinstance(other, TimingPoint):
            return other.__lt__(self)
        return False

    def __le__(self, other):
        return not self.__gt__(other)

    def __ge__(self, other):
        return not self.__lt__(other)

    def before(self, other):
        if isinstance(other, TimingPoint):
            return self.__lt__(other)
        elif isinstance(other, TimingInterval):
            return other.after(self)
        return False

    def after(self, other):
        if isinstance(other, TimingPoint):
            return self.__gt__(other)
        elif isinstance(other, TimingInterval):
            return other.before(self)
        return False


# TODO KV comments
# TODO KV - for parameter modules and x-slots
# in order to represent a "whole sign" timing interval (no matter how many x-slots long), use
#   TimingInterval(TimingPoint(0, 0), TimingPoint(0, 1))
class TimingInterval:

    # startpt (type TimingPoint) = the point at which this xslot interval begins
    # endpt (type TimingPoint) = the point at which this xslot interval ends
    def __init__(self, startpt, endpt):
        self.setinterval(startpt, endpt)

    @property
    def startpoint(self):
        return self._startpoint

    @property
    def endpoint(self):
        return self._endpoint

    def points(self):
        return self.startpoint(), self.endpoint()

    def setinterval(self, startpt, endpt):
        if startpt <= endpt:
            self._startpoint = startpt
            self._endpoint = endpt
        else:
            print("error: start point is larger than endpoint", startpt, endpt)
            # TODO KV throw an error?

    def ispoint(self):
        return self._startpoint == self._endpoint

    def before(self, other):
        if isinstance(other, TimingPoint):
            return self.endpoint < other
        elif isinstance(other, TimingInterval):
            if other.ispoint():
                return self.endpoint < other.startpoint
            elif not self.ispoint():
                return self.endpoint <= other.startpoint
            else:
                return other.after(self)
        return False

    def after(self, other):
        if isinstance(other, TimingPoint):
            return self.startpoint > other
        elif isinstance(other, TimingInterval):
            if other.ispoint():
                return self.startpoint > other.endpoint
            elif not self.ispoint():
                return self.startpoint >= other.endpoint
            else:
                return other.before(self)
        return False

    def adjacent(self, other):
        if isinstance(other, TimingInterval):
            return self.endpoint.equivalent(other.startpoint) or other.endpoint.equivalent(self.startpoint)
        return False

    def __eq__(self, other):
        if isinstance(other, TimingInterval):
            return self.startpoint == other.startpoint and self.endpoint == other.endpoint
        return False

    def overlapsinterval(self, other):
        if isinstance(other, TimingInterval):
            if self.iswholesign() or other.iswholesign():
                return True
            # either other starts at or in self, or self starts at or in other
            elif (self.startpoint <= other.startpoint and self.endpoint > other.startpoint) or (other.startpoint <= self.startpoint and other.endpoint > self.startpoint):
                return True
        return False
    
    
    def includesinterval(self, other):
        if isinstance(other, TimingInterval):
            if self.iswholesign() or other.iswholesign():
                return True
            elif (self.startpoint <= other.startpoint and self.endpoint > other.startpoint):
                return True
        return False


    def iswholesign(self):
        return self.startpoint == TimingPoint(0, 0) and self.endpoint == TimingPoint(0, 1)

    # TODO KV - overlapping and/or containing checking methods?

    def __repr__(self):
        return '<TimingInterval: ' + repr(self._startpoint) + ', ' + repr(self._endpoint) + '>'


class AddedInfo:

    def __init__(self,
                 iconic_flag=False, iconic_note="",
                 uncertain_flag=False, uncertain_note="",
                 estimated_flag=False, estimated_note="",
                 notspecified_flag=False, notspecified_note="",
                 variable_flag=False, variable_note="",
                 exceptional_flag=False, exceptional_note="",
                 incomplete_flag=False, incomplete_note="",
                 other_flag=False, other_note=""):

        self._iconic_flag = iconic_flag
        self._uncertain_flag = uncertain_flag
        self._iconic_note = iconic_note
        self._uncertain_note = uncertain_note
        self._estimated_flag = estimated_flag
        self._estimated_note = estimated_note
        self._notspecified_flag = notspecified_flag
        self._notspecified_note = notspecified_note
        self._variable_flag = variable_flag
        self._variable_note = variable_note
        self._exceptional_flag = exceptional_flag
        self._exceptional_note = exceptional_note
        self._incomplete_flag = incomplete_flag
        self._incomplete_note = incomplete_note
        self._other_flag = other_flag
        self._other_note = other_note

    def __eq__(self, other):
        if isinstance(other, AddedInfo):
            self_attributes = self.__dict__
            other_attributes = other.__dict__
            return False not in [self_attributes[attr] == other_attributes[attr] for attr in self_attributes.keys()]
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def iconic_flag(self):
        if not hasattr(self, '_iconic_flag'):
            # for backward compatibility pre-20230718 addition of 'Iconic' option
            self._iconic_flag = False  # default value
        return self._iconic_flag

    @iconic_flag.setter
    def iconic_flag(self, iconic_flag):
        self._iconic_flag = iconic_flag

    @property
    def iconic_note(self):
        if not hasattr(self, '_iconic_note'):
            # for backward compatibility pre-20230718 addition of 'Iconic' option
            self._iconic_note = ""  # default value
        return self._iconic_note

    @iconic_note.setter
    def iconic_note(self, iconic_note):
        self._iconic_note = iconic_note

    @property
    def uncertain_flag(self):
        return self._uncertain_flag

    @uncertain_flag.setter
    def uncertain_flag(self, uncertain_flag):
        self._uncertain_flag = uncertain_flag

    @property
    def uncertain_note(self):
        return self._uncertain_note

    @uncertain_note.setter
    def uncertain_note(self, uncertain_note):
        self._uncertain_note = uncertain_note

    @property
    def estimated_flag(self):
        return self._estimated_flag

    @estimated_flag.setter
    def estimated_flag(self, estimated_flag):
        self._estimated_flag = estimated_flag

    @property
    def estimated_note(self):
        return self._estimated_note

    @estimated_note.setter
    def estimated_note(self, estimated_note):
        self._estimated_note = estimated_note

    @property
    def notspecified_flag(self):
        return self._notspecified_flag

    @notspecified_flag.setter
    def notspecified_flag(self, notspecified_flag):
        self._notspecified_flag = notspecified_flag

    @property
    def notspecified_note(self):
        return self._notspecified_note

    @notspecified_note.setter
    def notspecified_note(self, notspecified_note):
        self._notspecified_note = notspecified_note

    @property
    def variable_flag(self):
        return self._variable_flag

    @variable_flag.setter
    def variable_flag(self, variable_flag):
        self._variable_flag = variable_flag

    @property
    def variable_note(self):
        return self._variable_note

    @variable_note.setter
    def variable_note(self, variable_note):
        self._variable_note = variable_note

    @property
    def exceptional_flag(self):
        return self._exceptional_flag

    @exceptional_flag.setter
    def exceptional_flag(self, exceptional_flag):
        self._exceptional_flag = exceptional_flag

    @property
    def incomplete_flag(self):
        return self._incomplete_flag

    @incomplete_flag.setter
    def incomplete_flag(self, incomplete_flag):
        self._incomplete_flag = incomplete_flag

    @property
    def exceptional_note(self):
        return self._exceptional_note

    @exceptional_note.setter
    def exceptional_note(self, exceptional_note):
        self._exceptional_note = exceptional_note

    @property
    def incomplete_note(self):
        return self._incomplete_note

    @incomplete_note.setter
    def incomplete_note(self, incomplete_note):
        self._incomplete_note = incomplete_note

    @property
    def other_flag(self):
        return self._other_flag

    @other_flag.setter
    def other_flag(self, other_flag):
        self._other_flag = other_flag

    @property
    def other_note(self):
        return self._other_note

    @other_note.setter
    def other_note(self, other_note):
        self._other_note = other_note

    def __repr__(self):
        reprstr = '<AddedInfo: '
        reprstr += 'Iconic (' + repr(int(self.iconic_flag)) + ' / ' + repr(self.iconic_note) + ') '
        reprstr += 'Uncertain (' + repr(int(self.uncertain_flag)) + ' / ' + repr(self.uncertain_note) + ') '
        reprstr += 'Estimated (' + repr(int(self.estimated_flag)) + ' / ' + repr(self.estimated_note) + ') '
        reprstr += 'Not specified (' + repr(int(self.notspecified_flag)) + ' / ' + repr(self.notspecified_note) + ') '
        reprstr += 'Variable (' + repr(int(self.variable_flag)) + ' / ' + repr(self.variable_note) + ') '
        reprstr += 'Exceptional (' + repr(int(self.exceptional_flag)) + ' / ' + repr(self.exceptional_note) + ') '
        reprstr += 'Incomplete (' + repr(int(self.incomplete_flag)) + ' / ' + repr(self.incomplete_note) + ') '
        reprstr += 'Other (' + repr(int(self.other_flag)) + ' / ' + repr(self.other_note) + ')'
        reprstr += '>'
        return reprstr

    def hascontent(self):
        hasflag = self.iconic_flag or self.uncertain_flag or self.estimated_flag or self.notspecified_flag or self.variable_flag or self.exceptional_flag or self.incomplete_flag or self.other_flag
        noteslength = len(
            (
                    self.iconic_note +
                    self.uncertain_note +
                    self.estimated_note +
                    self.notspecified_note +
                    self.variable_note +
                    self.exceptional_note +
                    self.incomplete_note +
                    self.other_note
            ).replace(" ", ""))
        return hasflag or noteslength > 0


class Signtype:

    def __init__(self, specslist, addedinfo=None):
        # specslist is a list of pairs:
        #   the first element is the full signtype property (correlated with radio buttons in selector dialog)
        #   the second element is a flag indicating whether or not to include this abbreviation in the concise form
        self._specslist = specslist
        self._addedinfo = addedinfo if addedinfo is not None else AddedInfo()

    @property
    def addedinfo(self):
        if not hasattr(self, '_addedinfo'):
            # for backward compatibility
            self._addedinfo = AddedInfo()
        return self._addedinfo

    @addedinfo.setter
    def addedinfo(self, addedinfo):
        self._addedinfo = addedinfo if addedinfo is not None else AddedInfo()

    @property
    def specslist(self):
        return self._specslist

    @specslist.setter
    def specslist(self, specslist):
        self._specslist = specslist

    def getabbreviation(self):
        abbrevsdict = self.convertspecstodict()
        abbreviationtext = self.makeabbreviationstring(abbrevsdict)
        abbreviationtext = abbreviationtext.strip()[1:-1]  # effectively remove the top-level ()'s
        return abbreviationtext

    def makeabbreviationstring(self, abbrevsdict):
        if abbrevsdict == {}:
            return ""
        else:
            abbrevlist = []
            abbrevstr = ""
            for k in abbrevsdict.keys():
                abbrevlist.append(k + self.makeabbreviationstring(abbrevsdict[k]))
            abbrevstr += "; ".join(abbrevlist)
            return " (" + abbrevstr + ")"

    def convertspecstodict(self):
        abbrevsdict = {}
        specscopy = [duple for duple in self._specslist]
        for duple in specscopy:
            if duple[1]:  # this is the flag to include the abbreviation in the concise form
                pathlist = duple[0].split('.')  # this is the path of abbreviations to this particular setting
                self.ensurepathindict(pathlist, abbrevsdict)
        return abbrevsdict

    def ensurepathindict(self, pathelements, abbrevsdict):
        if len(pathelements) > 0:
            if pathelements[0] not in abbrevsdict.keys():
                abbrevsdict[pathelements[0]] = {}
            self.ensurepathindict(pathelements[1:], abbrevsdict[pathelements[0]])


class BodypartInfo:

    def __init__(self, bodyparttype, bodyparttreemodel=None, addedinfo=None):
        self._addedinfo = addedinfo or AddedInfo()
        self._uniqueid = datetime.timestamp(datetime.now())
        self._bodyparttreemodel = bodyparttreemodel
        self._bodyparttype = bodyparttype

    @property
    def bodyparttreemodel(self):
        return self._bodyparttreemodel

    @bodyparttreemodel.setter
    def bodyparttreemodel(self, bodyparttreemodel):
        self._bodyparttreemodel = bodyparttreemodel

    @property
    def bodyparttype(self):
        return self._bodyparttype

    @bodyparttype.setter
    def bodyparttype(self, bodyparttype):
        self._bodyparttype = bodyparttype

    @property
    def addedinfo(self):
        return self._addedinfo

    @addedinfo.setter
    def addedinfo(self, addedinfo):
        self._addedinfo = addedinfo

    @property
    def uniqueid(self):
        return self._uniqueid

    @uniqueid.setter
    def uniqueid(self, uniqueid):
        self._uniqueid = uniqueid

    # returns true iff the instance has some specified content beyond its "blank" initial state
    # this could mean some addedinfo and/or treemodel content
    def hascontent(self):
        hasaddedinfo = self._addedinfo.hascontent()
        hastreecontent = self._bodyparttreemodel.hasselections()
        return hasaddedinfo or hastreecontent

    def __eq__(self, other):
        if isinstance(other, BodypartInfo):
            if self._addedinfo == other.addedinfo and self._bodyparttreemodel == other.bodyparttreemodel and self._bodyparttype == other.bodyparttype:
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def getabbreviation(self):
        # TODO KV implement
        return "Bodypart abbreviations not yet implemented"


# This module stores the location information for a particular articulator/s.
# It offers the user different location types (on body, in signing space), location options, and
# (for body-referenced locations) specific surfaces and/or subareas.
# It also stores "Added Info" (estimated, uncertain, etc) characteristics for each selected location
# as well as for the module overall.
class LocationModule(ParameterModule):
    def __init__(self, locationtreemodel, articulators, timingintervals=None, phonlocs=None, addedinfo=None, inphase=0):
        self._locationtreemodel = locationtreemodel
        self._inphase = inphase  # TODO KV is "inphase" actually the best name for this attribute?
        super().__init__(articulators, timingintervals=timingintervals, phonlocs=phonlocs, addedinfo=addedinfo)

    @property
    def locationtreemodel(self):
        return self._locationtreemodel

    @locationtreemodel.setter
    def locationtreemodel(self, locationtreemodel):
        self._locationtreemodel = locationtreemodel

    @property
    def inphase(self):
        return self._inphase

    @inphase.setter
    def inphase(self, inphase):
        self._inphase = inphase

    def getabbreviation(self):
        return "Location abbreviations not yet implemented"


class RelationX:

    def __init__(self, h1=False, h2=False, both=False, connected=False, arm1=False, arm2=False, leg1=False, leg2=False, other=False, othertext=""):
        self._h1 = h1
        self._h2 = h2
        self._both = both
        self._connected = connected
        self._arm1 = arm1
        self._arm2 = arm2
        self._leg1 = leg1
        self._leg2 = leg2
        self._other = other
        self._othertext = othertext

    def __eq__(self, other):
        if isinstance(other, RelationX):
            self_attributes = self.__dict__
            other_attributes = other.__dict__
            return False not in [self_attributes[attr] == other_attributes[attr] for attr in self_attributes.keys()]
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def displaystr(self):
        relX_str = ""
        if self.connected:
            relX_str = "X: both connected"
        elif self.other:
            relX_str = "X: other"
            if len(self.othertext) > 0:
                relX_str += " (" + self.othertext + ")"
        else:
            rel_dict = self.__dict__
            for attr in rel_dict:
                if rel_dict[attr]:
                    relX_str = "X: " + attr[1:] # attributes are prepended with _
                    break
        return relX_str

    @property
    def h1(self):
        return self._h1

    @h1.setter
    def h1(self, h1):
        self._h1 = h1

        if h1:
            self._h2 = False
            self._both = False
            self._arm1 = False
            self._arm2 = False
            self._leg1 = False
            self._leg2 = False
            self._other = False

    @property
    def h2(self):
        return self._h2

    @h2.setter
    def h2(self, h2):
        self._h2 = h2

        if h2:
            self._h1 = False
            self._arm1 = False
            self._arm2 = False
            self._leg1 = False
            self._leg2 = False
            self._both = False
            self._other = False

    @property
    def both(self):
        return self._both

    @both.setter
    def both(self, both):
        self._both = both

        if both:
            self._h1 = False
            self._h2 = False
            self._arm1 = False
            self._arm2 = False
            self._leg1 = False
            self._leg2 = False
            self._other = False

    @property
    def connected(self):
        return self._connected

    @connected.setter
    def connected(self, connected):
        self._connected = connected

        if connected:
            self.both = True

    @property
    def arm1(self):
        return self._arm1

    @arm1.setter
    def arm1(self, arm1):
        self._arm1 = arm1

        if arm1:
            self._h1 = False
            self._h2 = False
            self._both = False
            self._arm2 = False
            self._leg1 = False
            self._leg2 = False
            self._other = False

    @property
    def arm2(self):
        return self._arm2

    @arm2.setter
    def arm2(self, arm2):
        self._arm2 = arm2

        if arm2:
            self._h1 = False
            self._h2 = False
            self._both = False
            self._arm1 = False
            self._leg1 = False
            self._leg2 = False
            self._other = False

    @property
    def leg1(self):
        return self._leg1

    @leg1.setter
    def leg1(self, leg1):
        self._leg1 = leg1

        if leg1:
            self._h1 = False
            self._h2 = False
            self._both = False
            self._arm1 = False
            self._arm2 = False
            self._leg2 = False
            self._other = False

    @property
    def leg2(self):
        return self._leg2

    @leg2.setter
    def leg2(self, leg2):
        self._leg2 = leg2

        if leg2:
            self._h1 = False
            self._h2 = False
            self._both = False
            self._arm1 = False
            self._arm2 = False
            self._leg1 = False
            self._other = False

    @property
    def other(self):
        return self._other

    @other.setter
    def other(self, other):
        self._other = other

        if other:
            self._h1 = False
            self._h2 = False
            self._both = False
            self._arm1 = False
            self._arm2 = False
            self._leg1 = False
            self._leg2 = False

    @property
    def othertext(self):
        return self._othertext

    @othertext.setter
    def othertext(self, othertext):
        self._othertext = othertext

class RelationY:

    def __init__(self, h2=False, arm2=False, leg1=False, leg2=False, existingmodule=False, linkedmoduletype=None, linkedmoduleids=None, other=False, othertext=""):
        self._h2 = h2
        self._arm2 = arm2
        self._leg1 = leg1
        self._leg2 = leg2
        self._existingmodule = existingmodule
        self._linkedmoduletype = linkedmoduletype
        self._linkedmoduleids = linkedmoduleids or [0.0]
        self._other = other
        self._othertext = othertext

    def __eq__(self, other):
        if isinstance(other, RelationY):
            self_attributes = self.__dict__
            other_attributes = other.__dict__
            return False not in [self_attributes[attr] == other_attributes[attr] for attr in self_attributes.keys()]
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def displaystr(self):
        relY_str = ""
        if self.existingmodule:
            relY_str = "Y: existing module"
            if self.linkedmoduletype is not None:
                if self.linkedmoduletype == ModuleTypes.MOVEMENT:
                    relY_str += " (mvmt)"
                else:
                    relY_str += " (locn)"
        elif self.other: 
            relY_str = "Y: other"
            if len(self.othertext) > 0:
                relY_str += " (" + self.othertext + ")"
        else:
            rel_dict = self.__dict__
            for attr in "_h2", "_arm2", "_leg1", "_leg2":
                if rel_dict[attr]:
                    relY_str = "Y: " + attr[1:] # attributes are prepended with _
                    break    
        return relY_str

    @property
    def h2(self):
        return self._h2

    @h2.setter
    def h2(self, h2):
        self._h2 = h2

        if h2:
            self._arm2 = False
            self._leg1 = False
            self._leg2 = False
            self._existingmodule = False
            self._other = False

    @property
    def arm2(self):
        return self._arm2

    @arm2.setter
    def arm2(self, arm2):
        self._arm2 = arm2

        if arm2:
            self._h2 = False
            self._leg1 = False
            self._leg2 = False
            self._existingmodule = False
            self._other = False

    @property
    def leg1(self):
        return self._leg1

    @leg1.setter
    def leg1(self, leg1):
        self._leg1 = leg1

        if leg1:
            self._h2 = False
            self._arm2 = False
            self._leg2 = False
            self._existingmodule = False
            self._other = False

    @property
    def leg2(self):
        return self._leg2

    @leg2.setter
    def leg2(self, leg2):
        self._leg2 = leg2

        if leg2:
            self._h2 = False
            self._arm2 = False
            self._leg1 = False
            self._existingmodule = False
            self._other = False

    @property
    def existingmodule(self):
        return self._existingmodule

    @existingmodule.setter
    def existingmodule(self, existingmodule):
        self._existingmodule = existingmodule

        if existingmodule:
            self._h2 = False
            self._arm2 = False
            self._leg1 = False
            self._leg2 = False
            self._other = False

    @property
    def linkedmoduletype(self):
        return self._linkedmoduletype

    @linkedmoduletype.setter
    def linkedmoduletype(self, linkedmoduletype):
        # TODO KV validate?
        self._linkedmoduletype = linkedmoduletype

    @property
    def linkedmoduleids(self):
        return self._linkedmoduleids

    @linkedmoduleids.setter
    def linkedmoduleids(self, linkedmoduleids):
        # TODO KV validate?
        self._linkedmoduleids = linkedmoduleids

    @property
    def other(self):
        return self._other

    @other.setter
    def other(self, other):
        self._other = other

        if other:
            self._h2 = False
            self._arm2 = False
            self._leg1 = False
            self._leg2 = False
            self._existingmodule = False

    @property
    def othertext(self):
        return self._othertext

    @othertext.setter
    def othertext(self, othertext):
        self._othertext = othertext


class RelationModule(ParameterModule):

    def __init__(self, relationx, relationy, bodyparts_dict, contactrel, xy_crossed, xy_linked, directionslist, articulators, timingintervals=None, phonlocs=None, addedinfo=None):
        self._relationx = relationx or RelationX()
        self._relationy = relationy or RelationY()
        self._bodyparts_dict = {}
        for bodypart in bodyparts_dict.keys():
            if bodypart not in self._bodyparts_dict.keys():
                self._bodyparts_dict[bodypart] = {}
            for n in bodyparts_dict[bodypart].keys():
                self._bodyparts_dict[bodypart][n] = bodyparts_dict[bodypart][n] or BodypartInfo(bodyparttype=bodypart, bodyparttreemodel=None)
        self._contactrel = contactrel or ContactRelation()
        self._xy_crossed = xy_crossed
        self._xy_linked = xy_linked
        self._directions = directionslist or [
            Direction(axis=Direction.HORIZONTAL),
            Direction(axis=Direction.VERTICAL),
            Direction(axis=Direction.SAGITTAL),
        ]
        super().__init__(articulators, timingintervals=timingintervals, phonlocs=phonlocs, addedinfo=addedinfo)

    @property
    def relationx(self):
        return self._relationx

    @relationx.setter
    def relationx(self, relationx):
        self._relationx = relationx

    @property
    def relationy(self):
        return self._relationy

    @relationy.setter
    def relationy(self, relationy):
        self._relationy = relationy

    @property
    def bodyparts_dict(self):
        return self._bodyparts_dict

    @bodyparts_dict.setter
    def bodyparts_dict(self, bodyparts_dict):
        self._bodyparts_dict = bodyparts_dict

    @property
    def contactrel(self):
        return self._contactrel

    @contactrel.setter
    def contactrel(self, contactrel):
        self._contactrel = contactrel

    @property
    def xy_crossed(self):
        return self._xy_crossed

    @xy_crossed.setter
    def xy_crossed(self, xy_crossed):
        self._xy_crossed = xy_crossed

    @property
    def xy_linked(self):
        return self._xy_linked

    @xy_linked.setter
    def xy_linked(self, xy_linked):
        self._xy_linked = xy_linked

    @property
    def directions(self):
        return self._directions

    @directions.setter
    def directions(self, directions):
        self._directions = directions
    
    def get_paths(self):
        paths = {}
        arts, nums = self.get_articulators_in_use()
        for i in range(len(arts)):
            bodypartinfo = self.bodyparts_dict[arts[i]][nums[i]]
            treemodel = bodypartinfo.bodyparttreemodel
            paths.update({arts[i]: treemodel.get_checked_items()})
        return paths
    
    def has_direction(self, axisnum): # returns true if suboptions of direction are selected
        dir = self.directions[axisnum]
        return dir.plus or dir.minus or dir.inline
    
    def usesarticulator(self, articulator, artnum=None):
        articulators_in_use = {1: False, 2: False}
        if articulator == HAND:
            articulators_in_use = self.hands_in_use()
        elif articulator == ARM:
            articulators_in_use = self.arms_in_use()
        elif articulator == LEG:
            articulators_in_use = self.legs_in_use()

        if artnum is None:
            return articulators_in_use[1] or articulators_in_use[2]
        else:
            return articulators_in_use[artnum]
        
    def no_selections(self):
        for d in self.directions:
            if d.axisselected:
                return False
            
        return (self.contactrel.contact == None and not self.xy_crossed and not self.xy_linked)
    
    def get_articulators_in_use(self):
        a = []
        n = []
        for b in [HAND, ARM, LEG]:
            for i in [1,2]:
                if self.usesarticulator(b,i):
                    a.append(b)
                    n.append(i)
        return a, n

    def hands_in_use(self):
        return {
            1: self.relationx.both or self.relationx.h1,
            2: self.relationx.both or self.relationx.h2 or self.relationy.h2
        }

    def arms_in_use(self):
        return {
            1: self.relationx.arm1,
            2: self.relationx.arm2 or self.relationy.arm2
        }

    def legs_in_use(self):
        return {
            1: self.relationx.leg1 or self.relationy.leg1,
            2: self.relationx.leg2 or self.relationy.leg2
        }

    def getabbreviation(self):
        # TODO implement
        return "Relation abbreviations not yet implemented"


class MannerRelation:
    def __init__(self, holding=False, continuous=False, intermittent=False):
        self._holding = holding
        self._continuous = continuous
        self._intermittent = intermittent

    def __eq__(self, other):
        if isinstance(other, MannerRelation):
            if self._holding == other.holding and self._continuous == other.continuous and self._intermittent == other.intermittent:
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        repr_str = "nil"
        if self._holding:
            repr_str = "holding"
        elif self._continuous:
            repr_str = "continuous"
        elif self._intermittent:
            repr_str = "intermittent"

        return '<MannerRelation: ' + repr(repr_str) + '>'
    

    @property
    def holding(self):
        return self._holding

    @holding.setter
    def holding(self, checked):
        self._holding = checked

        if checked:
            self._continuous = False
            self._intermittent = False

    @property
    def continuous(self):
        return self._continuous

    @continuous.setter
    def continuous(self, checked):
        self._continuous = checked

        if checked:
            self._holding = False
            self._intermittent = False

    @property
    def intermittent(self):
        return self._intermittent

    @intermittent.setter
    def intermittent(self, checked):
        self._intermittent = checked

        if checked:
            self._continuous = False
            self._holding = False


class ContactRelation:
    def __init__(self, contact=None, contacttype=None, mannerrel=None, distance_list=None):
        self._contact = contact
        self._contacttype = contacttype
        self._manner = mannerrel
        self._distances = distance_list or [
            Distance(Direction.HORIZONTAL),
            Distance(Direction.VERTICAL),
            Distance(Direction.SAGITTAL)
        ]

    def __eq__(self, other):
        if isinstance(other, ContactRelation):
            self_attributes = self.__dict__
            other_attributes = other.__dict__
            return False not in [self_attributes[attr] == other_attributes[attr] for attr in self_attributes.keys()]
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        repr_str = "nil"
        if self._contact:
            repr_str = "yes"
            if self._contacttype:
                repr_str += " " + repr(self._contacttype)
            if self._manner:
                repr_str += ", " + repr(self._manner)
        elif not self._contact:
            repr_str = "no"
            if self._distances:
                distance_str_list = [repr(axis_dist for axis_dist in self._distances)]
                repr_str += ", ".join([""] + distance_str_list)

        return '<ContactRelation: ' + repr(repr_str) + '>'

    def has_manner(self):
        return self.manner.holding or self.manner.intermittent or self.manner.continuous

    def has_contacttype(self):
        return self.contacttype.light or self.contacttype.firm or self.contacttype.other
    @property
    def contact(self):
        return self._contact

    @contact.setter
    def contact(self, hascontact):
        self._contact = hascontact

    @property
    def contacttype(self):
        return self._contacttype

    @contacttype.setter
    def contacttype(self, contacttype):
        self._contacttype = contacttype

    @property
    def manner(self):
        return self._manner

    @manner.setter
    def manner(self, mannerrel):
        self._manner = mannerrel

    @property
    def distances(self):
        return self._distances

    @distances.setter
    def distances(self, distances):
        self._distances = distances


class ContactType:
    def __init__(self, light=False, firm=False, other=False, othertext=""):
        self._light = light
        self._firm = firm
        self._other = other
        self._othertext = othertext

    def __eq__(self, other):
        if isinstance(other, ContactType):
            self_attributes = self.__dict__
            other_attributes = other.__dict__
            return False not in [self_attributes[attr] == other_attributes[attr] for attr in self_attributes.keys()]
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        repr_str = "nil"
        if self._light:
            repr_str = "light"
        elif self._firm:
            repr_str = "firm"
        elif self._other:
            repr_str = "other"
            if len(self._othertext) > 0:
                repr_str += " " + self._othertext

        return '<ContactType: ' + repr(repr_str) + '>'

    @property
    def light(self):
        return self._light

    @light.setter
    def light(self, checked):
        self._light = checked

        if checked:
            self._firm = False
            self._other = False
            self._othertext = ""

    @property
    def firm(self):
        return self._firm

    @firm.setter
    def firm(self, checked):
        self._firm = checked

        if checked:
            self._light = False
            self._other = False
            self._othertext = ""

    @property
    def other(self):
        return self._other

    @other.setter
    def other(self, checked):
        self._other = checked

        if checked:
            self._light = False
            self._firm = False

    @property
    def othertext(self):
        return self._othertext

    @othertext.setter
    def othertext(self, othertext):
        self._othertext = othertext


# This class is used by the Relation Module to track the axis on which to measure the relation between
# two elements (X and Y), as well as the direction of X relative to Y.
class Direction:
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    SAGITTAL = "sagittal"

    def __init__(self, axis, axisselected=False, plus=False, minus=False, inline=False):
        self._axis = axis
        self._axisselected = axisselected
        self._plus = plus  # ipsi for horizontal, above for vertical, distal for sagittal
        self._minus = minus  # contra for horizontal, below for vertical, proximal for sagittal
        self._inline = inline  # in line with (for all axes)

    def __eq__(self, other):
        if isinstance(other, Direction):
            if self._axis == other.axis and self._axisselected == other.axisselected and self._plus == other.plus and self._minus == other.minus and self._inline == other.inline:
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        plus_label = "plus"
        minus_label = "minus"
        inline_label = "in line"
        if self._axis == Direction.HORIZONTAL:
            plus_label = "ipsi"
            minus_label = "contra"
        elif self._axis == Direction.VERTICAL:
            plus_label = "above"
            minus_label = "below"
        elif self._axis == Direction.SAGITTAL:
            plus_label = "distal"
            minus_label = "proximal"

        repr_str = self._axis
        if self._axisselected:
            repr_str += " selected"
            if self._plus:
                repr_str += " / " + plus_label
            elif self._minus:
                repr_str += " / " + minus_label
            elif self._inline:
                repr_str += " / " + inline_label
        else:
            repr_str += " unselected"

        return '<Direction: ' + repr(repr_str) + '>'

    @property
    def axis(self):
        return self._axis

    @axis.setter
    def axis(self, axis):
        self._axis = axis

    @property
    def axisselected(self):
        return self._axisselected

    @axisselected.setter
    def axisselected(self, isselected):
        self._axisselected = isselected

    @property
    def plus(self):
        return self._plus

    @plus.setter
    def plus(self, isplus):
        self._plus = isplus

        if isplus:
            self._minus = False
            self._inline = False

    @property
    def minus(self):
        return self._minus

    @minus.setter
    def minus(self, isminus):
        self._minus = isminus

        if isminus:
            self._plus = False
            self._inline = False

    @property
    def inline(self):
        return self._inline

    @inline.setter
    def inline(self, isinline):
        self._inline = isinline

        if isinline:
            self._plus = False
            self._minus = False


# This class is used by the Relation Module to track the axis on which to measure the relation between
# two elements (X and Y), as well as the relative distance between those two elements.
class Distance:

    def __init__(self, axis, close=False, medium=False, far=False):
        self._axis = axis
        self._close = close
        self._medium = medium
        self._far = far

    def __eq__(self, other):
        if isinstance(other, Distance):
            if self._axis == other.axis and self._close == other.close and self._medium == other.medium and self._far == other.far:
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def has_selection(self):
        return self.close or self.medium or self.far

    @property
    def axis(self):
        return self._axis

    @axis.setter
    def axis(self, axis):
        self._axis = axis

    @property
    def close(self):
        return self._close

    @close.setter
    def close(self, isclose):
        self._close = isclose

        if isclose:
            self._far = False
            self._medium = False

    @property
    def medium(self):
        return self._medium

    @medium.setter
    def medium(self, ismedium):
        self._medium = ismedium

        if ismedium:
            self._close = False
            self._far = False

    @property
    def far(self):
        return self._far

    @far.setter
    def far(self, isfar):
        self._far = isfar

        if isfar:
            self._close = False
            self._medium = False


# This module stores the absolute orientation of a particular hand/s.
# It includes specifications for palm and root directions.
# It also stores "Added Info" (estimated, uncertain, etc) characteristics for the module overall.
class OrientationModule(ParameterModule):
    def __init__(self, palmdirs_list, rootdirs_list, articulators, timingintervals=None, phonlocs=None, addedinfo=None):
        self._palm = palmdirs_list or [
            Direction(axis=Direction.HORIZONTAL),
            Direction(axis=Direction.VERTICAL),
            Direction(axis=Direction.SAGITTAL)
        ]
        self._root = rootdirs_list or [
            Direction(axis=Direction.HORIZONTAL),
            Direction(axis=Direction.VERTICAL),
            Direction(axis=Direction.SAGITTAL)
        ]

        super().__init__(articulators, timingintervals=timingintervals, phonlocs=phonlocs, addedinfo=addedinfo)

    @property
    def palm(self):
        return self._palm

    @palm.setter
    def palm(self, palm):
        self._palm = palm

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, root):
        self._root = root

    def getabbreviation(self):
        # TODO implement
        return "Orientation abbreviations not yet implemented"


# This module stores the transcription of one hand's configuration.
# It includes specifications for each slot in each field, as well as whether the forearm is involved.
# It also stores "Added Info" (estimated, uncertain, etc) characteristics for each slot,
# forearm, and the hand config overall.
class HandConfigurationModule(ParameterModule):
    def __init__(self, handconfiguration, overalloptions, articulators, timingintervals=None, phonlocs=None, addedinfo=None):
        self._handconfiguration = handconfiguration
        self._overalloptions = overalloptions
        super().__init__(articulators, timingintervals=timingintervals, phonlocs=phonlocs, addedinfo=addedinfo)

    @property
    def handconfiguration(self):
        return self._handconfiguration

    @handconfiguration.setter
    def handconfiguration(self, new_handconfiguration):
        self._handconfiguration = new_handconfiguration

    @property
    def overalloptions(self):
        return self._overalloptions

    @overalloptions.setter
    def overalloptions(self, new_overalloptions):
        self._overalloptions = new_overalloptions

    def getabbreviation(self):
        handconfighand = HandConfigurationHand(self.handconfiguration)

        predefinedname = ""
        txntuple = tuple(HandConfigurationHand(self.handconfiguration).get_hand_transcription_list())
        if txntuple in PREDEFINED_MAP.keys():
            predefinedname = "'" + PREDEFINED_MAP[txntuple].name + "' "

        fieldstext = ""
        fields = [handconfighand.field2, handconfighand.field3, handconfighand.field4, handconfighand.field5, handconfighand.field6, handconfighand.field7]
        for field in fields:
            fieldstext += "["
            for slot in iter(field):
                fieldstext += slot.symbol
            fieldstext += "] "

        return predefinedname + fieldstext

        
# This class consists of six fields (2 through 7; 1 is forearm and is not included here) that store
# the transcription info for one hand configuration.
class HandConfigurationHand:
    def __init__(self, fields):
        self.field2, self.field3, self.field4, self.field5, self.field6, self.field7 = [HandConfigurationField(field['field_number'], field['slots']) for field in fields]

    def __iter__(self):
        return chain(iter(self.field2), iter(self.field3), iter(self.field4), iter(self.field5), iter(self.field6), iter(self.field7))

    def __eq__(self, other):
        if isinstance(other, HandConfigurationHand):
            self_attributes = self.__dict__
            other_attributes = other.__dict__
            return False not in [self_attributes[attr] == other_attributes[attr] for attr in self_attributes.keys()]
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_hand_transcription_list(self):
        return [slot.symbol for slot in self.__iter__()]

    def get_hand_transcription_string(self):
        return ''.join(self.get_hand_transcription_list())

    def is_empty(self):
        return self.get_hand_transcription_list() == [
            '', '', '', '',
            '', '', NULL, '/', '', '', '', '', '', '',
            '1', '', '', '',
            '', '2', '', '', '',
            '', '3', '', '', '',
            '', '4', '', '', ''
        ]


class NonManualModule(ParameterModule):
    def __init__(self, nonman_specs, articulators, timingintervals=None, phonlocs=None, addedinfo=None):
        self._nonmanual = nonman_specs
        super().__init__(articulators, timingintervals=timingintervals, phonlocs=phonlocs, addedinfo=addedinfo)
        pass


# This class consists of 34 slots; each instance of a HandConfigurationField corresponds to a certain subset
# of slots. The slots store the transcription info for one field in a hand configuration.
class HandConfigurationField:
    def __init__(self, field_number, slots):
        self._field_number = field_number
        self._slots = slots

        self.set_slots()

    def __eq__(self, other):
        if isinstance(other, HandConfigurationField):
            self_attributes = self.__dict__
            other_attributes = other.__dict__
            return False not in [self_attributes[attr] == other_attributes[attr] for attr in self_attributes.keys()]
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def field_number(self):
        return self._field_number

    @field_number.setter
    def field_number(self, new_field_number):
        self._field_number = new_field_number

    def set_slots(self):
        if self._field_number == 2:
            self.slot2, self.slot3, self.slot4, self.slot5 = [HandConfigurationSlot(slot['slot_number'], slot['symbol'], slot['addedinfo']) for slot in self._slots]
        elif self._field_number == 3:
            self.slot6, self.slot7, self.slot8, self.slot9, self.slot10, self.slot11, self.slot12, self.slot13, self.slot14, self.slot15 = [HandConfigurationSlot(slot['slot_number'], slot['symbol'], slot['addedinfo']) for slot in self._slots]
        elif self._field_number == 4:
            self.slot16, self.slot17, self.slot18, self.slot19 = [HandConfigurationSlot(slot['slot_number'], slot['symbol'], slot['addedinfo']) for slot in self._slots]
        elif self._field_number == 5:
            self.slot20, self.slot21, self.slot22, self.slot23, self.slot24 = [HandConfigurationSlot(slot['slot_number'], slot['symbol'], slot['addedinfo']) for slot in self._slots]
        elif self._field_number == 6:
            self.slot25, self.slot26, self.slot27, self.slot28, self.slot29 = [HandConfigurationSlot(slot['slot_number'], slot['symbol'], slot['addedinfo']) for slot in self._slots]
        elif self._field_number == 7:
            self.slot30, self.slot31, self.slot32, self.slot33, self.slot34 = [HandConfigurationSlot(slot['slot_number'], slot['symbol'], slot['addedinfo']) for slot in self._slots]

    def __iter__(self):
        if self._field_number == 2:
            return [self.slot2, self.slot3, self.slot4, self.slot5].__iter__()
        elif self._field_number == 3:
            return [self.slot6, self.slot7, self.slot8, self.slot9, self.slot10, self.slot11, self.slot12, self.slot13, self.slot14, self.slot15].__iter__()
        elif self._field_number == 4:
            return [self.slot16, self.slot17, self.slot18, self.slot19].__iter__()
        elif self._field_number == 5:
            return [self.slot20, self.slot21, self.slot22, self.slot23, self.slot24].__iter__()
        elif self._field_number == 6:
            return [self.slot25, self.slot26, self.slot27, self.slot28, self.slot29].__iter__()
        elif self._field_number == 7:
            return [self.slot30, self.slot31, self.slot32, self.slot33, self.slot34].__iter__()


# This class represents the transcription for one single field of a hand configuration.
# It also contains the "Added Info" (uncertain, estimated, etc) for the slot.
class HandConfigurationSlot:
    def __init__(self, slot_number, symbol, addedinfo):
        self._slot_number = slot_number
        self._symbol = symbol
        self._addedinfo = addedinfo if addedinfo is not None else AddedInfo()

    def __eq__(self, other):
        if isinstance(other, HandConfigurationSlot):
            self_attributes = self.__dict__
            other_attributes = other.__dict__
            return False not in [self_attributes[attr] == other_attributes[attr] for attr in self_attributes.keys()]
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def addedinfo(self):
        return self._addedinfo

    @addedinfo.setter
    def addedinfo(self, addedinfo):
        self._addedinfo = addedinfo if addedinfo is not None else AddedInfo()

    @property
    def slot_number(self):
        return self._slot_number

    @slot_number.setter
    def slot_number(self, new_slot_number):
        self._slot_number = new_slot_number

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, new_symbol):
        self._symbol = new_symbol


# This class is used to define the underlying structure for a particular sign's timing info.
# It consists of three values:
#   (1) the number of whole x-slots for the sign,
#   (2) a list of fractional divisions (eg 1/2, 1/3, 1/4) that should be made available to the user to select when
#       specifying timing information for the sign's modules
#   (3) the (optional) additional fraction of an x-slot to include for the sign, on top of the specified whole number
class XslotStructure:

    def __init__(self, number=1, fractionalpoints=None, additionalfraction=Fraction()):
        # integer
        self._number = number
        # list of Fractions objects = the fractions of whole xslots to display and make available to select
        self._fractionalpoints = [] if fractionalpoints is None else fractionalpoints
        # Fraction object = the additional part of an x-slot on top of the wholes
        self._additionalfraction = additionalfraction

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, number):
        self._number = number

    @property
    def fractionalpoints(self):
        return self._fractionalpoints

    @fractionalpoints.setter
    def fractionalpoints(self, fractionalpoints):
        self._fractionalpoints = fractionalpoints

    @property
    def additionalfraction(self):
        return self._additionalfraction

    @additionalfraction.setter
    def additionalfraction(self, additionalfraction):
        self._additionalfraction = additionalfraction
