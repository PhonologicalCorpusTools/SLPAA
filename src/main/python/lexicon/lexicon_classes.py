from itertools import chain
from fractions import Fraction
# from datetime import datetime
# from copy import deepcopy
from datetime import datetime

from gui.movement_view import MovementTree
from gui.xslots_selector import XslotStructure
from lexicon.module_classes import MovementModule, HandConfigurationModule, ParameterModule, TimingInterval, TimingPoint, LocationModule

NULL = '\u2205'


def empty_copy(obj):
    class Empty(obj.__class__):
        def __init__(self): pass
    new_copy = Empty(  )
    new_copy.__class__ = obj.__class__
    return new_copy


class SignLevelInformation:
    def __init__(self, signlevel_info=None, serializedsignlevelinfo=None):
        # self.settings = app_settings
        if serializedsignlevelinfo is not None:
            self._entryid = serializedsignlevelinfo['entryid']
            self._gloss = serializedsignlevelinfo['gloss']
            self._lemma = serializedsignlevelinfo['lemma']
            self._source = serializedsignlevelinfo['source']
            self._signer = serializedsignlevelinfo['signer']
            self._frequency = serializedsignlevelinfo['frequency']
            self._coder = serializedsignlevelinfo['coder']
            # self._update_date = signlevel_info['date']
            self._datecreated = datetime.fromtimestamp(serializedsignlevelinfo['date created'])
            self._datelastmodified = datetime.fromtimestamp(serializedsignlevelinfo['date last modified'])
            self._note = serializedsignlevelinfo['note']
            self._handdominance = serializedsignlevelinfo['handdominance']
        elif signlevel_info is not None:
            self._entryid = signlevel_info['entryid']
            self._gloss = signlevel_info['gloss']
            self._lemma = signlevel_info['lemma']
            self._source = signlevel_info['source']
            self._signer = signlevel_info['signer']
            self._frequency = signlevel_info['frequency']
            self._coder = signlevel_info['coder']
            # self._update_date = signlevel_info['date']
            self._datecreated = signlevel_info['date created']
            self._datelastmodified = signlevel_info['date last modified']
            self._note = signlevel_info['note']
            self._handdominance = signlevel_info['handdominance']
        else:
            print("TODO KV no sign level info; what to do?")

    def __eq__(self, other):
        aresame = True
        if isinstance(other, SignLevelInformation):
            if self._entryid != other.entryid or self._gloss != other.gloss or self._lemma != other.lemma:
                aresame = False
            if self._source != other.source or self._signer != other.signer or self._frequency != other.frequency:
                aresame = False
            if self._coder != other.coder or self._datecreated != other.datecreated or self._datelastmodified != other.datelastmodified:
                aresame = False
            if self._note != other.note or self._handdominance != other.handdominance:
                aresame = False
        else:
            aresame = False
        return aresame

    def serialize(self):
        return {
            'entryid': self._entryid,
            'gloss': self._gloss,
            'lemma': self._lemma,
            'source': self._source,
            'signer': self._signer,
            'frequency': self._frequency,
            'coder': self._coder,
            'date created': self._datecreated.timestamp(),
            'date last modified': self._datelastmodified.timestamp(),
            'note': self._note,
            'handdominance': self._handdominance
        }

    @property
    def entryid(self):
        return self._entryid

    @entryid.setter
    def entryid(self, new_entryid):
        self._entryid = new_entryid
    #
    # def entryid_string(self):
    #     numdigits = self.settings['display']['entryid_digits']
    #     entryid_string = str(self._entryid)
    #     entryid_string = "0"*(numdigits-len(entryid_string)) + entryid_string
    #     return entryid_string

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
    #
    # @property
    # def update_date(self):
    #     return self._update_date
    #
    # @update_date.setter
    # def update_date(self, new_update_date):
    #     self._update_date = new_update_date

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
    def signtype(self):
        return self._signtype

    @signtype.setter
    def signtype(self, new_signtype):
        self._signtype = new_signtype

    @property
    def handdominance(self):
        return self._handdominance

    @handdominance.setter
    def handdominance(self, new_handdominance):
        self._handdominance = new_handdominance


class GlobalHandshapeInformation:
    def __init__(self, global_handshape_info):
        self._forearm = global_handshape_info['forearm']
        self._estimated = global_handshape_info['estimated']
        self._uncertain = global_handshape_info['uncertain']
        self._incomplete = global_handshape_info['incomplete']
        self._fingerspelled = global_handshape_info['fingerspelled']
        self._initialized = global_handshape_info['initialized']

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

    @property
    def fingerspelled(self):
        return self._fingerspelled

    @fingerspelled.setter
    def fingerspelled(self, new_is_fingerspelled):
        self._fingerspelled = new_is_fingerspelled

    @property
    def initialized(self):
        return self._initialized

    @initialized.setter
    def initialized(self, new_is_initialized):
        self._initialized = new_is_initialized

    @property
    def forearm(self):
        return self._forearm

    @forearm.setter
    def forearm(self, new_is_forearm):
        self._forearm = new_is_forearm


class HandConfiguration:
    def __init__(self, config):

        # from above
        # self.hand1 = HandConfigurationHand(hand['fields'])
        self.config = config


class LocationPoint:
    def __init__(self, location_point_info):
        self.points = location_point_info
        #self.loc_identifier = location_point_info['image']
        #self.point = Point(location_point_info['point']) if location_point_info['point'] else None


class LocationHand:
    def __init__(self, location_hand_info):
        self.contact = location_hand_info['contact']
        self.D = LocationPoint(location_hand_info['D'])
        self.W = LocationPoint(location_hand_info['W'])


class LocationTranscription:
    def __init__(self, location_transcription_info):
        self.start = LocationHand(location_transcription_info['start'])
        self.end = LocationHand(location_transcription_info['end'])

        #self.parts = {name: LocationHand(hand) for name, hand in location_transcription_info.items()}

# TODO: need to think about duplicated signs
class Sign:
    """
    Gloss in signlevel_information is used as the unique key
    """
    def __init__(self, signlevel_info=None, serializedsign=None):
        if serializedsign is not None:
            self._signlevel_information = SignLevelInformation(serializedsignlevelinfo=serializedsign['signlevel'])
            # self._datecreated = serializedsign['date created']
            # self._datelastmodified = serializedsign['date last modified']
            self._signtype = serializedsign['type']
            self._xslotstructure = serializedsign['xslot structure']
            self._specifiedxslots = serializedsign['specified xslots']
            self.unserializemovementmodules(serializedsign['mov modules'])
            self.handpartmodules = serializedsign['hpt modules']
            self.locationmodules = serializedsign['loc modules']
            self.contactmodules = serializedsign['con modules']
            self.orientationmodules = serializedsign['ori modules']
            self.handconfigmodules = serializedsign['cfg modules']
        else:
            self._signlevel_information = signlevel_info
            # self._datecreated = int(datetime.timestamp(datetime.now()))
            # self.lastmodifiednow()
            self._signtype = None
            self._xslotstructure = XslotStructure()
            self._specifiedxslots = False
            self.movementmodules = {}
            self.handpartmodules = {}
            self.locationmodules = {}
            self.contactmodules = {}
            self.orientationmodules = {}
            self.handconfigmodules = {}

    def serialize(self):
        return {
            'signlevel': self._signlevel_information.serialize(),
            # 'date created': self._datecreated,
            # 'date last modified': self._datelastmodified,
            'type': self._signtype,
            'xslot structure': self.xslotstructure,
            'specified xslots': self.specifiedxslots,
            'mov modules': self.serializemovementmodules(),
            'hpt modules': self.handpartmodules,
            'loc modules': self.locationmodules,
            'con modules': self.contactmodules,
            'ori modules': self.orientationmodules,
            'cfg modules': self.handconfigmodules
        }

    def serializemovementmodules(self):
        serialized = {}
        for k in self.movementmodules.keys():
            serialized[k] = MovementTree(self.movementmodules[k])
        return serialized

    def unserializemovementmodules(self, serialized_mvmtmodules):
        unserialized = {}
        for k in serialized_mvmtmodules.keys():
            mvmttreemodel = serialized_mvmtmodules[k].getMovementTreeModel()
            hands = serialized_mvmtmodules[k].hands
            timingintervals = serialized_mvmtmodules[k].timingintervals
            unserialized[k] = MovementModule(mvmttreemodel, hands, timingintervals)
        self.movementmodules = unserialized

    def __hash__(self):
        # return hash(self.signlevel_information.gloss)
        return hash(self.signlevel_information.entryid)

    # Ref: https://eng.lyft.com/hashing-and-equality-in-python-2ea8c738fb9d
    def __eq__(self, other):
        # return isinstance(other, Sign) and self.signlevel_information.gloss == other.signlevel_information.gloss
        return isinstance(other, Sign) and self.signlevel_information.entryid == other.signlevel_information.entryid

    def __repr__(self):
        return '<SIGN: ' + repr(self.signlevel_information.gloss) + ' - ' + repr(self.signlevel_information.entryid) + '>'

    @property
    def signlevel_information(self):
        return self._signlevel_information

    @signlevel_information.setter
    def signlevel_information(self, signlevelinfo):
        self._signlevel_information = signlevelinfo  # SignLevelInformation(signlevelinfo)

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, locn):
        self._location = LocationTranscription(locn)

    @property
    def specifiedxslots(self):
        return self._specifiedxslots

    @specifiedxslots.setter
    def specifiedxslots(self, specifiedxslots):
        self._specifiedxslots = specifiedxslots
    #
    # @property
    # def datecreated(self):
    #     return self._datecreated
    #
    # # input should be an integer timestamp
    # @datecreated.setter
    # def datecreated(self, created):
    #     # TODO KV - validate?
    #     self._datecreated = created
    #
    # @property
    # def datelastmodified(self):
    #     return self._datelastmodified
    #
    # # input should be an integer timestamp
    # @datelastmodified.setter
    # def signtype(self, lastmodified):
    #     # TODO KV - validate?
    #     self._datelastmodified = lastmodified

    def lastmodifiednow(self):
        # self._datelastmodified = int(datetime.timestamp(datetime.now()))
        self.signlevel_information.lastmodifiednow()

    @property
    def signtype(self):
        return self._signtype

    @signtype.setter
    def signtype(self, stype):
        # TODO KV - validate?
        self._signtype = stype

    @property
    def xslotstructure(self):
        return self._xslotstructure

    @xslotstructure.setter
    def xslotstructure(self, xslotstruct):
        # TODO KV - validate?
        self._xslotstructure = xslotstruct

    def updatemovementmodule(self, uniqueid, movementtree, hands_dict, timingintervals):
        mvmtmod = self.movementmodules[uniqueid]
        ischanged = False
        if mvmtmod.movementtreemodel != movementtree:
            mvmtmod.movementtreemodel = movementtree
            ischanged = True
        if mvmtmod.hands != hands_dict:
            mvmtmod.hands = hands_dict
            ischanged = True
        if mvmtmod.timingintervals != timingintervals:
            mvmtmod.timingintervals = timingintervals
            ischanged = True
        if ischanged:
            self.lastmodifiednow()

    def addmovementmodule(self, movementtree, hands_dict, timingintervals):
        # create and add a brand new one
        mvmtmod = MovementModule(movementtree, hands_dict, timingintervals)
        self.movementmodules[mvmtmod.uniqueid] = mvmtmod
        self.lastmodifiednow()

    def removemovementmodule(self, uniqueid):
        self.movementmodules.pop(uniqueid)
        self.lastmodifiednow()

    def updatehandconfigmodule(self, uniqueid, handconfiguration, overalloptions, hands_dict, timingintervals):
        hcfgmod = self.handconfigmodules[uniqueid]
        ischanged = False
        if hcfgmod.handconfiguration != handconfiguration:
            hcfgmod.handconfiguration = handconfiguration
            ischanged = True
        if hcfgmod.hands != hands_dict:
            hcfgmod.hands = hands_dict
            ischanged = True
        if hcfgmod.overalloptions != overalloptions:
            hcfgmod.overalloptions = overalloptions
            ischanged = True
        if hcfgmod.timingintervals != timingintervals:
            hcfgmod.timingintervals = timingintervals
            ischanged = True
        if ischanged:
            self.lastmodifiednow()

    def addhandconfigmodule(self, handconfiguration, overalloptions, hands_dict, timingintervals):
        # create and add a brand new one
        hcfgmod = HandConfigurationModule(handconfiguration, overalloptions, hands_dict, timingintervals)
        self.handconfigmodules[hcfgmod.uniqueid] = hcfgmod
        self.lastmodifiednow()

    def removehandconfigmodule(self, uniqueid):
        self.handconfigmodules.pop(uniqueid)
        self.lastmodifiednow()

    def addtargetmodule(self, targetmod):
        self.targetmodules.append(targetmod)
        self.lastmodifiednow()

    def addlocationmodule(self, locationtree, hands_dict, timingintervals):
        # create and add a brand new one
        locnmod = LocationModule(locationtree, hands_dict, timingintervals)
        self.locationmodules[locnmod.uniqueid] = locnmod
        self.lastmodifiednow()

    def addorientationmodule(self, orientationmod):
        self.orientationmodules.append(orientationmod)
        self.lastmodifiednow()

    def gettimedmodules(self):
        return [self.movementmodules, self.handpartmodules, self.locationmodules, self.contactmodules, self.orientationmodules, self.handconfigmodules]


class Corpus:
    #TODO: need a default for location_definition
    def __init__(self, name="", signs=None, location_definition=None, path=None, serializedcorpus=None, highestID=0):  # movement_definition=None,
        if serializedcorpus:
            self.name = serializedcorpus['name']
            self.signs = set([Sign(serializedsign=s) for s in serializedcorpus['signs']])
            self.location_definition = serializedcorpus['loc defn']
            # self.movement_definition = serializedcorpus['mvmt defn']
            self.path = serializedcorpus['path']
            self.highestID = serializedcorpus['highest id']
        else:
            self.name = name
            self.signs = signs if signs else set()
            self.location_definition = location_definition
            # self.movement_definition = movement_definition
            self.path = path
            self.highestID = highestID

    def serialize(self):
        return {
            'name': self.name,
            'signs': [s.serialize() for s in list(self.signs)],
            'loc defn': self.location_definition,
            'path': self.path,
            'highest id': self.highestID
        }

    def get_sign_glosses(self):
        return sorted([sign.signlevel_information.gloss for sign in self.signs])

    def get_previous_sign(self, gloss):
        sign_glosses = self.get_sign_glosses()
        current_index = sign_glosses.index(gloss)

        # if the very first sign is selected, then return the one after it, otherwise the previous one
        previous_gloss = sign_glosses[current_index-1] if current_index-1 >= 0 else sign_glosses[1]

        return self.get_sign_by_gloss(previous_gloss)

    def get_sign_by_gloss(self, gloss):
        # Every sign has a unique gloss, so this function will always return one sign
        for sign in self.signs:
            if sign.signlevel_information.gloss == gloss:
                return sign

    def add_sign(self, new_sign):
        self.signs.add(new_sign)
        self.highestID = max([new_sign.signlevel_information.entryid, self.highestID])

    def remove_sign(self, trash_sign):
        self.signs.remove(trash_sign)

    def __contains__(self, item):
        return item in self.signs

    def __iter__(self):
        return iter(self.signs)

    def __len__(self):
        return len(self.signs)

    def __repr__(self):
        return '<CORPUS: ' + repr(self.name) + '>'


if __name__ == '__main__':

    # test TimingPoint
    print("testing TimingPoint comparison operators...")
    tp1 = TimingPoint(1, Fraction(0))
    tp2 = TimingPoint(1, Fraction(1,3))
    tp3 = TimingPoint(1, Fraction(3,4))
    tp4 = TimingPoint(1, Fraction(1))
    tp5 = TimingPoint(2, Fraction(0))
    tp6 = TimingPoint(2, Fraction(1,3))
    tp7 = TimingPoint(2, Fraction(1,3))
    orderedpoints1 = [tp1, tp2, tp3, tp4, tp6]
    orderedpoints2 = [tp1, tp2, tp3, tp5, tp7]
    lt_success = True
    le_success = True
    ge_success = True
    gt_success = True
    eq_success = True
    ne_success = True
    equiv_success = True
    for tplist in [orderedpoints1, orderedpoints2]:
        for idx, first in enumerate(tplist[:-1]):
            for second in tplist[idx+1:]:
                lt_success = lt_success and first < second
                gt_success = gt_success and second > first
                le_success = le_success and first <= second
                ge_success = ge_success and second >= first
                eq_success = eq_success and not first == second
                ne_success = ne_success and first != second
                equiv_success = equiv_success and not first.equivalent(second)
    lt_success = lt_success and not tp6 < tp7 and not tp4 < tp5
    gt_success = gt_success and not tp6 > tp7 and not tp5 > tp4
    le_success = le_success and tp6 <= tp7 and tp4 <= tp5
    ge_success = ge_success and tp6 >= tp7 and tp4 >= tp5
    eq_success = eq_success and tp6 == tp7 and not tp4 == tp5
    ne_success = ne_success and not tp6 != tp7 and tp4 != tp5
    equiv_success = equiv_success and tp6.equivalent(tp7) and tp4.equivalent(tp5)

    print("success: lt", lt_success, "/ gt", gt_success, "/ le", le_success, "/ ge", ge_success, "/ eq", eq_success, "/ ne", ne_success, "/ equiv", equiv_success)


    # test TimingInterval
    print("testing TimingInterval methods...")
    int1 = TimingInterval(tp1, tp2)
    int2 = TimingInterval(tp2, tp4)
    int3 = TimingInterval(tp5, tp6)
    int4 = TimingInterval(tp1, tp7)
    int5 = TimingInterval(tp4, tp4)
    int6 = TimingInterval(tp5, tp1)
    int7 = TimingInterval(tp7, tp7)

    containssuccess = True
    containssuccess = containssuccess and not int1.containsinterval(int2) and not int2.containsinterval(
        int4) and int4.containsinterval(int1) and int4.containsinterval(int3) and int4.containsinterval(int5)
    ispointsuccess = int7.ispoint() and not int1.ispoint()
    print("success: containsinterval", containssuccess, "/ ispoint", ispointsuccess)

    # test ParameterModule
    print("testing ParameterModule methods...")
    pm1 = ParameterModule(hands={"H1": True, "H2": True}, timingintervals=[int1])
    print(pm1.timingintervals)
    pm2 = ParameterModule(hands={"H1": True, "H2": False}, timingintervals=[int1, int2])
    print(pm2.timingintervals)
    pm3 = ParameterModule(hands={"H1": True, "H2": False}, timingintervals=[int1, int2, int3])
    print(pm3.timingintervals)
    pm4 = ParameterModule(hands={"H1": True, "H2": False}, timingintervals=[int1, int3])
    print(pm4.timingintervals)
    pm5 = ParameterModule(hands={"H1": True, "H2": False}, timingintervals=[int1, int2, int7])
    print(pm5.timingintervals)
