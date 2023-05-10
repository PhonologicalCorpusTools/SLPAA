from models.movement_models import MovementTreeModel
from serialization.serialization_classes import LocationModuleSerializable, MovementModuleSerializable
from lexicon.module_classes import SignLevelInformation, MovementModule, AddedInfo, LocationModule
from gui.signtypespecification_view import Signtype
from gui.xslotspecification_view import XslotStructure
from models.location_models import LocationTreeModel

NULL = '\u2205'


def empty_copy(obj):
    class Empty(obj.__class__):
        def __init__(self): pass
    new_copy = Empty(  )
    new_copy.__class__ = obj.__class__
    return new_copy


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
            signtype = serializedsign['type']
            self._signtype = Signtype(signtype.specslist) if signtype is not None else None
            if hasattr(serializedsign['type'], '_addedinfo'):  # for backward compatibility
                self._signtype.addedinfo = serializedsign['type'].addedinfo
            self._xslotstructure = serializedsign['xslot structure']
            self._specifiedxslots = serializedsign['specified xslots']
            self.unserializemovementmodules(serializedsign['mov modules'])
            self.handpartmodules = serializedsign['hpt modules']
            self.unserializelocationmodules(serializedsign['loc modules'])
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
            'loc modules': self.serializelocationmodules(),
            'con modules': self.contactmodules,
            'ori modules': self.orientationmodules,
            'cfg modules': self.handconfigmodules
        }

    # TODO KV - can the un/serialization methods below be combined into generic ones that can be used for all model-based modules?

    def serializemovementmodules(self):
        serialized = {}
        for k in self.movementmodules.keys():
            serialized[k] = MovementModuleSerializable(self.movementmodules[k])
        return serialized

    def unserializemovementmodules(self, serialized_mvmtmodules):
        unserialized = {}
        for k in serialized_mvmtmodules.keys():
            serialmodule = serialized_mvmtmodules[k]
            # print('unserializing movement module', serialmodule.movementtree)
            # print(serialmodule.movementtree.checkstates)
            # if hasattr(serialmodule.movementtree, 'userspecifiedvalues'):
            #     print(serialmodule.movementtree.userspecifiedvalues)
            mvmttreemodel = MovementTreeModel(serialmodule.movementtree)
            hands = serialmodule.hands
            inphase = serialmodule.inphase if (hasattr(serialmodule, 'inphase') and serialmodule.inphase is not None) else 0
            timingintervals = serialmodule.timingintervals
            addedinfo = serialmodule.addedinfo if hasattr(serialmodule, 'addedinfo') else AddedInfo()  # TODO KV for backwards compatibility with pre-20230208 movement modules
            unserialized[k] = MovementModule(mvmttreemodel, hands, timingintervals, addedinfo, inphase)
        self.movementmodules = unserialized

    def serializelocationmodules(self):
        serialized = {}
        for k in self.locationmodules.keys():
            serialized[k] = LocationModuleSerializable(self.locationmodules[k])
        return serialized

    def unserializelocationmodules(self, serialized_locnmodules):
        unserialized = {}
        for k in serialized_locnmodules.keys():
            serialmodule = serialized_locnmodules[k]
            locntreemodel = LocationTreeModel(serialmodule.locationtree)
            hands = serialmodule.hands
            timingintervals = serialmodule.timingintervals
            addedinfo = serialmodule.addedinfo if hasattr(serialmodule, 'addedinfo') else AddedInfo()  # TODO KV for backwards compatibility with pre-20230208 movement modules
            phonlocs = serialmodule.phonlocs
            inphase = serialmodule.inphase if hasattr(serialmodule, 'inphase') else 0  # TODO KV for backwards compatibility with pre-20230410 location modules
            unserialized[k] = LocationModule(locntreemodel, hands, timingintervals, addedinfo, phonlocs=phonlocs, inphase=inphase)
        self.locationmodules = unserialized

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

    # def updatemovementmodule(self, uniqueid, movementtree, hands_dict, timingintervals, addedinfo, inphase):
    #     mvmtmod = self.movementmodules[uniqueid]
    #     ischanged = False
    #     if mvmtmod.movementtreemodel != movementtree:
    #         mvmtmod.movementtreemodel = movementtree
    #         ischanged = True
    #     if mvmtmod.hands != hands_dict:
    #         mvmtmod.hands = hands_dict
    #         ischanged = True
    #     if mvmtmod.timingintervals != timingintervals:
    #         mvmtmod.timingintervals = timingintervals
    #         ischanged = True
    #     if mvmtmod.inphase != inphase:
    #         mvmtmod.inphase = inphase
    #         ischanged = True
    #     if mvmtmod.addedinfo != addedinfo:
    #         mvmtmod.addedinfo = addedinfo
    #         ischanged = True
    #     if ischanged:
    #         self.lastmodifiednow()

    def updatemovementmodule(self, uniqueid, updated_mvmtmod):
        current_mvmtmod = self.movementmodules[uniqueid]
        ischanged = False
        if current_mvmtmod.movementtreemodel != updated_mvmtmod.movementtreemodel:
            current_mvmtmod.movementtreemodel = updated_mvmtmod.movementtreemodel
            ischanged = True
        if current_mvmtmod.hands != updated_mvmtmod.hands:
            current_mvmtmod.hands = updated_mvmtmod.hands
            ischanged = True
        if current_mvmtmod.timingintervals != updated_mvmtmod.timingintervals:
            current_mvmtmod.timingintervals = updated_mvmtmod.timingintervals
            ischanged = True
        if current_mvmtmod.inphase != updated_mvmtmod.inphase:
            current_mvmtmod.inphase = updated_mvmtmod.inphase
            ischanged = True
        if current_mvmtmod.addedinfo != updated_mvmtmod.addedinfo:
            current_mvmtmod.addedinfo = updated_mvmtmod.addedinfo
            ischanged = True
        if ischanged:
            self.lastmodifiednow()

    # def addmovementmodule(self, movementtree, hands_dict, timingintervals, addedinfo, inphase):
    #     # create and add a brand new one
    #     mvmtmod = MovementModule(movementtree, hands_dict, timingintervals, addedinfo, inphase)
    #     self.movementmodules[mvmtmod.uniqueid] = mvmtmod
    #     self.lastmodifiednow()

    def addmovementmodule(self, mvmtmod):
        # create and add a brand new one
        # mvmtmod = MovementModule(movementtree, hands_dict, timingintervals, addedinfo, inphase)
        self.movementmodules[mvmtmod.uniqueid] = mvmtmod
        self.lastmodifiednow()

    def removemovementmodule(self, uniqueid):
        self.movementmodules.pop(uniqueid)
        self.lastmodifiednow()

    # def updatehandconfigmodule(self, uniqueid, handconfiguration, overalloptions, hands_dict, timingintervals, addedinfo):
    #     hcfgmod = self.handconfigmodules[uniqueid]
    #     ischanged = False
    #     if hcfgmod.handconfiguration != handconfiguration:
    #         hcfgmod.handconfiguration = handconfiguration
    #         ischanged = True
    #     if hcfgmod.hands != hands_dict:
    #         hcfgmod.hands = hands_dict
    #         ischanged = True
    #     if hcfgmod.overalloptions != overalloptions:
    #         hcfgmod.overalloptions = overalloptions
    #         ischanged = True
    #     if hcfgmod.timingintervals != timingintervals:
    #         hcfgmod.timingintervals = timingintervals
    #         ischanged = True
    #     if hcfgmod.addedinfo != addedinfo:
    #         hcfgmod.addedinfo = addedinfo
    #         ischanged = True
    #     if ischanged:
    #         self.lastmodifiednow()

    def updatehandconfigmodule(self, uniqueid, updated_hcfgmod):
        current_hcfgmod = self.handconfigmodules[uniqueid]
        ischanged = False
        if current_hcfgmod.handconfiguration != updated_hcfgmod.handconfiguration:
            current_hcfgmod.handconfiguration = updated_hcfgmod.handconfiguration
            ischanged = True
        if current_hcfgmod.hands != updated_hcfgmod.hands:
            current_hcfgmod.hands = updated_hcfgmod.hands
            ischanged = True
        if current_hcfgmod.overalloptions != updated_hcfgmod.overalloptions:
            current_hcfgmod.overalloptions = updated_hcfgmod.overalloptions
            ischanged = True
        if current_hcfgmod.timingintervals != updated_hcfgmod.timingintervals:
            current_hcfgmod.timingintervals = updated_hcfgmod.timingintervals
            ischanged = True
        if current_hcfgmod.addedinfo != updated_hcfgmod.addedinfo:
            current_hcfgmod.addedinfo = updated_hcfgmod.addedinfo
            ischanged = True
        if ischanged:
            self.lastmodifiednow()

    # def addhandconfigmodule(self, handconfiguration, overalloptions, hands_dict, timingintervals, addedinfo):
    #     # create and add a brand new one
    #     hcfgmod = HandConfigurationModule(handconfiguration, overalloptions, hands_dict, timingintervals, addedinfo)
    #     self.handconfigmodules[hcfgmod.uniqueid] = hcfgmod
    #     self.lastmodifiednow()

    def addhandconfigmodule(self, hcfgmod):
        # create and add a brand new one
        # hcfgmod = HandConfigurationModule(handconfiguration, overalloptions, hands_dict, timingintervals, addedinfo)
        self.handconfigmodules[hcfgmod.uniqueid] = hcfgmod
        self.lastmodifiednow()

    def removehandconfigmodule(self, uniqueid):
        self.handconfigmodules.pop(uniqueid)
        self.lastmodifiednow()

    def addtargetmodule(self, targetmod):
        self.targetmodules.append(targetmod)
        self.lastmodifiednow()

    # def addlocationmodule(self, locationtree, hands_dict, timingintervals, addedinfo, phonlocs, loctype, inphase):
    #     # create and add a brand new one
    #     locnmod = LocationModule(locationtree, hands_dict, timingintervals, addedinfo, phonlocs=phonlocs, inphase=inphase)
    #     self.locationmodules[locnmod.uniqueid] = locnmod
    #     self.lastmodifiednow()

    def addlocationmodule(self, locnmod):
        # create and add a brand new one
        # locnmod = LocationModule(locationtree, hands_dict, timingintervals, addedinfo, phonlocs=phonlocs, inphase=inphase)
        self.locationmodules[locnmod.uniqueid] = locnmod
        self.lastmodifiednow()

    def removelocationmodule(self, uniqueid):
        self.locationmodules.pop(uniqueid)
        self.lastmodifiednow()

    # def updatelocationmodule(self, uniqueid, locationtree, hands_dict, timingintervals, addedinfo, phonlocs, loctype, inphase):
    #     locnmod = self.locationmodules[uniqueid]
    #     ischanged = False
    #     if locnmod.locationtreemodel != locationtree:
    #         locnmod.locationtreemodel = locationtree
    #         ischanged = True
    #     if locnmod.hands != hands_dict:
    #         locnmod.hands = hands_dict
    #         ischanged = True
    #     if locnmod.timingintervals != timingintervals:
    #         locnmod.timingintervals = timingintervals
    #         ischanged = True
    #     if locnmod.inphase != inphase:
    #         locnmod.inphase = inphase
    #         ischanged = True
    #     if locnmod.phonlocs != phonlocs:
    #         locnmod.phonlocs = phonlocs
    #         ischanged = True
    #     if locnmod.addedinfo != addedinfo:
    #         locnmod.addedinfo = addedinfo
    #         ischanged = True
    #     if ischanged:
    #         self.lastmodifiednow()

    def updatelocationmodule(self, uniqueid, updated_locnmod):
        current_locnmod = self.locationmodules[uniqueid]
        ischanged = False
        if current_locnmod.locationtreemodel != updated_locnmod.locationtreemodel:
            current_locnmod.locationtreemodel = updated_locnmod.locationtreemodel
            ischanged = True
        if current_locnmod.hands != updated_locnmod.hands:
            current_locnmod.hands = updated_locnmod.hands
            ischanged = True
        if current_locnmod.timingintervals != updated_locnmod.timingintervals:
            current_locnmod.timingintervals = updated_locnmod.timingintervals
            ischanged = True
        if current_locnmod.inphase != updated_locnmod.inphase:
            current_locnmod.inphase = updated_locnmod.inphase
            ischanged = True
        if current_locnmod.phonlocs != updated_locnmod.phonlocs:
            current_locnmod.phonlocs = updated_locnmod.phonlocs
            ischanged = True
        if current_locnmod.addedinfo != updated_locnmod.addedinfo:
            current_locnmod.addedinfo = updated_locnmod.addedinfo
            ischanged = True
        if ischanged:
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


# # TODO KV temporary testing function - delete eventually!
# if __name__ == '__main__':
#
#     # test TimingPoint
#     print("testing TimingPoint comparison operators...")
#     tp1 = TimingPoint(1, Fraction(0))
#     tp2 = TimingPoint(1, Fraction(1,3))
#     tp3 = TimingPoint(1, Fraction(3,4))
#     tp4 = TimingPoint(1, Fraction(1))
#     tp5 = TimingPoint(2, Fraction(0))
#     tp6 = TimingPoint(2, Fraction(1,3))
#     tp7 = TimingPoint(2, Fraction(1,3))
#     orderedpoints1 = [tp1, tp2, tp3, tp4, tp6]
#     orderedpoints2 = [tp1, tp2, tp3, tp5, tp7]
#     lt_success = True
#     le_success = True
#     ge_success = True
#     gt_success = True
#     eq_success = True
#     ne_success = True
#     equiv_success = True
#     for tplist in [orderedpoints1, orderedpoints2]:
#         for idx, first in enumerate(tplist[:-1]):
#             for second in tplist[idx+1:]:
#                 lt_success = lt_success and first < second
#                 gt_success = gt_success and second > first
#                 le_success = le_success and first <= second
#                 ge_success = ge_success and second >= first
#                 eq_success = eq_success and not first == second
#                 ne_success = ne_success and first != second
#                 equiv_success = equiv_success and not first.equivalent(second)
#     lt_success = lt_success and not tp6 < tp7 and not tp4 < tp5
#     gt_success = gt_success and not tp6 > tp7 and not tp5 > tp4
#     le_success = le_success and tp6 <= tp7 and tp4 <= tp5
#     ge_success = ge_success and tp6 >= tp7 and tp4 >= tp5
#     eq_success = eq_success and tp6 == tp7 and not tp4 == tp5
#     ne_success = ne_success and not tp6 != tp7 and tp4 != tp5
#     equiv_success = equiv_success and tp6.equivalent(tp7) and tp4.equivalent(tp5)
#
#     print("success: lt", lt_success, "/ gt", gt_success, "/ le", le_success, "/ ge", ge_success, "/ eq", eq_success, "/ ne", ne_success, "/ equiv", equiv_success)
#
#
#     # test TimingInterval
#     print("testing TimingInterval methods...")
#     int1 = TimingInterval(tp1, tp2)
#     int2 = TimingInterval(tp2, tp4)
#     int3 = TimingInterval(tp5, tp6)
#     int4 = TimingInterval(tp1, tp7)
#     int5 = TimingInterval(tp4, tp4)
#     int6 = TimingInterval(tp5, tp1)
#     int7 = TimingInterval(tp7, tp7)
#
#     containssuccess = True
#     containssuccess = containssuccess and not int1.containsinterval(int2) and not int2.containsinterval(
#         int4) and int4.containsinterval(int1) and int4.containsinterval(int3) and int4.containsinterval(int5)
#     ispointsuccess = int7.ispoint() and not int1.ispoint()
#     print("success: containsinterval", containssuccess, "/ ispoint", ispointsuccess)
#
#     # test ParameterModule
#     print("testing ParameterModule methods...")
#     pm1 = ParameterModule(hands={"H1": True, "H2": True}, timingintervals=[int1])
#     print(pm1.timingintervals)
#     pm2 = ParameterModule(hands={"H1": True, "H2": False}, timingintervals=[int1, int2])
#     print(pm2.timingintervals)
#     pm3 = ParameterModule(hands={"H1": True, "H2": False}, timingintervals=[int1, int2, int3])
#     print(pm3.timingintervals)
#     pm4 = ParameterModule(hands={"H1": True, "H2": False}, timingintervals=[int1, int3])
#     print(pm4.timingintervals)
#     pm5 = ParameterModule(hands={"H1": True, "H2": False}, timingintervals=[int1, int2, int7])
#     print(pm5.timingintervals)
