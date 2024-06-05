import logging
import os

from serialization_classes import LocationModuleSerializable, MovementModuleSerializable, RelationModuleSerializable
from lexicon.module_classes import SignLevelInformation, MovementModule, AddedInfo, LocationModule, ModuleTypes, BodypartInfo, RelationX, RelationY, Direction, RelationModule, treepathdelimiter
from gui.signtypespecification_view import Signtype
from gui.xslotspecification_view import XslotStructure
from models.movement_models import MovementTreeModel
from models.location_models import LocationTreeModel, BodypartTreeModel
from constant import HAND, ARM, LEG

NULL = '\u2205'
glossesdelimiter = " / "


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


class Sign:
    """
    EntryID in signlevel_information is used as the unique key
    """
    def __init__(self, signlevel_info=None, serializedsign=None):
        if signlevel_info is not None:
            signlevel_info.parentsign = self
        self._signlevel_information = signlevel_info
        self._signtype = None
        self._xslotstructure = XslotStructure()
        self._specifiedxslots = False
        self.movementmodules = {}
        self.movementmodulenumbers = {}
        self.handpartmodules = {}
        self.handpartmodulenumbers = {}
        self.locationmodules = {}
        self.locationmodulenumbers = {}
        self.relationmodules = {}
        self.relationmodulenumbers = {}
        self.orientationmodules = {}
        self.orientationmodulenumbers = {}
        self.handconfigmodules = {}
        self.handconfigmodulenumbers = {}

        if serializedsign is not None:
            self._signlevel_information = SignLevelInformation(serializedsignlevelinfo=serializedsign['signlevel'], parentsign=self)
            signtype = serializedsign['type']
            self._signtype = Signtype(signtype.specslist) if signtype is not None else None
            if hasattr(serializedsign['type'], '_addedinfo'):  # for backward compatibility
                self._signtype.addedinfo = serializedsign['type'].addedinfo
            self._xslotstructure = serializedsign['xslot structure']
            self._specifiedxslots = serializedsign['specified xslots']
            self.unserializemovementmodules(serializedsign['mov modules'])
            self.movementmodulenumbers = serializedsign['mov module numbers'] if 'mov module numbers' in serializedsign.keys() else self.numbermodules(ModuleTypes.MOVEMENT)
            # backward compatibility; also note relation must come before location
            self.unserializerelationmodules(serializedsign['rel modules' if 'rel modules' in serializedsign.keys() else 'con modules'])
            self.relationmodulenumbers = serializedsign['rel module numbers'] if 'rel module numbers' in serializedsign.keys() else self.numbermodules(ModuleTypes.RELATION)
            self.unserializelocationmodules(serializedsign['loc modules'])
            self.locationmodulenumbers = serializedsign['loc module numbers'] if 'loc module numbers' in serializedsign.keys() else self.numbermodules(ModuleTypes.LOCATION)
            self.orientationmodules = serializedsign['ori modules']
            self.orientationmodulenumbers = serializedsign['ori module numbers'] if 'ori module numbers' in serializedsign.keys() else self.numbermodules(ModuleTypes.ORIENTATION)
            self.handconfigmodules = serializedsign['cfg modules']
            self.handconfigmodulenumbers = serializedsign['cfg module numbers'] if 'cfg module numbers' in serializedsign.keys() else self.numbermodules(ModuleTypes.HANDCONFIG)

    def numbermodules(self, moduletype):
        moduledict = self.getmoduledict(moduletype)
        modulenumbersdict = {}
        modnum = 1
        for uid in moduledict:
            modulenumbersdict[uid] = modnum
            modnum += 1
        return modulenumbersdict

    def getmoduledict(self, moduletype):
        if moduletype == ModuleTypes.LOCATION:
            return self.locationmodules
        elif moduletype == ModuleTypes.MOVEMENT:
            return self.movementmodules
        elif moduletype == ModuleTypes.HANDCONFIG:
            return self.handconfigmodules
        elif moduletype == ModuleTypes.RELATION:
            return self.relationmodules
        elif moduletype == ModuleTypes.ORIENTATION:
            return self.orientationmodules
        else:
            return {}

    def getmodulenumbersdict(self, moduletype):
        if moduletype == ModuleTypes.LOCATION:
            return self.locationmodulenumbers
        elif moduletype == ModuleTypes.MOVEMENT:
            return self.movementmodulenumbers
        elif moduletype == ModuleTypes.HANDCONFIG:
            return self.handconfigmodulenumbers
        elif moduletype == ModuleTypes.RELATION:
            return self.relationmodulenumbers
        elif moduletype == ModuleTypes.ORIENTATION:
            return self.orientationmodulenumbers
        else:
            return {}

    def serialize(self):
        return {
            'signlevel': self._signlevel_information.serialize(),
            'type': self._signtype,
            'xslot structure': self.xslotstructure,
            'specified xslots': self.specifiedxslots,
            'mov modules': self.serializemovementmodules(),
            'mov module numbers': self.movementmodulenumbers,
            'loc modules': self.serializelocationmodules(),
            'loc module numbers': self.locationmodulenumbers,
            'rel modules': self.serializerelationmodules(),
            'rel module numbers': self.relationmodulenumbers,
            'ori modules': self.orientationmodules,
            'ori module numbers': self.orientationmodulenumbers,
            'cfg modules': self.handconfigmodules,
            'cfg module numbers': self.handconfigmodulenumbers,
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
            mvmttreemodel = MovementTreeModel(serialmodule.movementtree)
            articulators = serialmodule.articulators
            inphase = serialmodule.inphase if (hasattr(serialmodule, 'inphase') and serialmodule.inphase is not None) else 0
            timingintervals = serialmodule.timingintervals
            addedinfo = serialmodule.addedinfo if hasattr(serialmodule, 'addedinfo') else AddedInfo()  # for backward compatibility with pre-20230208 movement modules
            unserialized[k] = MovementModule(mvmttreemodel, articulators, timingintervals, addedinfo, inphase)
            unserialized[k].uniqueid = k
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
            articulators = serialmodule.articulators
            timingintervals = serialmodule.timingintervals
            addedinfo = serialmodule.addedinfo if hasattr(serialmodule, 'addedinfo') else AddedInfo()  # for backward compatibility with pre-20230208 movement modules
            phonlocs = serialmodule.phonlocs
            inphase = serialmodule.inphase if hasattr(serialmodule, 'inphase') else 0  # for backward compatibility with pre-20230410 location modules

            serialtree = serialmodule.locationtree

            # backward compatibility with corpora saved before Relation Module existed (June 2023)
            # if hasattr(serialtree.locationtype, '_axis') and serialtree.locationtype.axis:
            if serialtree.locationtype.allfalse() and "Horizontal" in serialtree.checkstates.keys() and "Vertical" in serialtree.checkstates.keys() and "Sagittal" in serialtree.checkstates.keys():
                # then this likely was saved as an "axis of relation" location module, which is now
                # deprecated and should be converted to a relation module

                # relation module should have X = H1 and Y = H2
                relation_x = RelationX(h1=True)
                relation_y = RelationY(h2=True)
                # relation module will have directions copied over from the original axis location tree
                dir_hor = Direction(Direction.HORIZONTAL)
                dir_ver = Direction(Direction.VERTICAL)
                dir_sag = Direction(Direction.SAGITTAL)
                for pathtext in serialtree.checkstates.keys():
                    if serialtree.checkstates[pathtext] > 0:  # if fully or partially checked
                        if "Horizontal" == pathtext:
                            dir_hor.axisselected = True
                        elif "Vertical" == pathtext:
                            dir_ver.axisselected = True
                        elif "Sagittal" == pathtext:
                            dir_sag.axisselected = True
                        elif "H1 is to H1 side of H2" in pathtext:
                            dir_hor.plus = True
                        elif "H1 is to H2 side of H2" in pathtext:
                            dir_hor.minus = True
                        elif "H1 is above H2" in pathtext:
                            dir_ver.plus = True
                        elif "H1 is below H2" in pathtext:
                            dir_ver.minus = True
                        elif "H1 is in front of H2" in pathtext or "H1 is more distal than H2" in pathtext:
                            dir_sag.plus = True
                        elif "H1 is behind H2" in pathtext or "H1 is more proximal than H2" in pathtext:
                            dir_sag.minus = True
                directions = [dir_hor, dir_ver, dir_sag]
                bodyparts_dict = {
                    HAND: {
                        1: BodypartInfo(bodyparttype=HAND, bodyparttreemodel=BodypartTreeModel(bodyparttype=HAND)),
                        2: BodypartInfo(bodyparttype=HAND, bodyparttreemodel=BodypartTreeModel(bodyparttype=HAND))
                    },
                    ARM: {
                        1: BodypartInfo(bodyparttype=ARM, bodyparttreemodel=BodypartTreeModel(bodyparttype=ARM)),
                        2: BodypartInfo(bodyparttype=ARM, bodyparttreemodel=BodypartTreeModel(bodyparttype=ARM))
                    },
                    LEG: {
                        1: BodypartInfo(bodyparttype=LEG, bodyparttreemodel=BodypartTreeModel(bodyparttype=LEG)),
                        2: BodypartInfo(bodyparttype=LEG, bodyparttreemodel=BodypartTreeModel(bodyparttype=LEG))
                    }
                }
                # relation module should not have contact or manner or distance specified
                convertedrelationmodule = RelationModule(relation_x, relation_y, bodyparts_dict=bodyparts_dict, contactrel=None, xy_crossed=False, xy_linked=False, directionslist=directions, articulators=None, timingintervals=timingintervals, addedinfo=addedinfo)
                self.addmodule(convertedrelationmodule, ModuleTypes.RELATION)

            else:
                locntreemodel = LocationTreeModel(serialmodule.locationtree)
                unserialized[k] = LocationModule(locntreemodel, articulators, timingintervals, addedinfo, phonlocs=phonlocs, inphase=inphase)
                unserialized[k].uniqueid = k
        self.locationmodules = unserialized

    def serializerelationmodules(self):
        serialized = {}
        for k in self.relationmodules.keys():
            serialized[k] = RelationModuleSerializable(self.relationmodules[k])
        return serialized

    def unserializerelationmodules(self, serialized_relmodules):
        unserialized = {}
        for k in serialized_relmodules.keys():
            serialmodule = serialized_relmodules[k]
            articulators = serialmodule.articulators
            timingintervals = serialmodule.timingintervals
            addedinfo = serialmodule.addedinfo if hasattr(serialmodule, 'addedinfo') else AddedInfo()
            relationx = serialmodule.relationx
            relationy = serialmodule.relationy
            bodyparts_dict = {
                HAND: {
                    1: BodypartInfo(
                        bodyparttype=HAND,
                        bodyparttreemodel=BodypartTreeModel(bodyparttype=HAND, serializedlocntree=serialmodule.bodyparts_dict[HAND][1].bodyparttree),
                        addedinfo=serialmodule.bodyparts_dict[HAND][1].addedinfo),
                    2: BodypartInfo(
                        bodyparttype=HAND,
                        bodyparttreemodel=BodypartTreeModel(bodyparttype=HAND, serializedlocntree=serialmodule.bodyparts_dict[HAND][2].bodyparttree),
                        addedinfo=serialmodule.bodyparts_dict[HAND][2].addedinfo),
                },
                ARM: {
                    1: BodypartInfo(
                        bodyparttype=ARM,
                        bodyparttreemodel=BodypartTreeModel(bodyparttype=ARM, serializedlocntree=serialmodule.bodyparts_dict[ARM][1].bodyparttree),
                        addedinfo=serialmodule.bodyparts_dict[ARM][1].addedinfo),
                    2: BodypartInfo(
                        bodyparttype=ARM,
                        bodyparttreemodel=BodypartTreeModel(bodyparttype=ARM, serializedlocntree=serialmodule.bodyparts_dict[ARM][2].bodyparttree),
                        addedinfo=serialmodule.bodyparts_dict[ARM][2].addedinfo),
                },
                LEG: {
                    1: BodypartInfo(
                        bodyparttype=LEG,
                        bodyparttreemodel=BodypartTreeModel(bodyparttype=LEG, serializedlocntree=serialmodule.bodyparts_dict[LEG][1].bodyparttree),
                        addedinfo=serialmodule.bodyparts_dict[LEG][1].addedinfo),
                    2: BodypartInfo(
                        bodyparttype=LEG,
                        bodyparttreemodel=BodypartTreeModel(bodyparttype=LEG, serializedlocntree=serialmodule.bodyparts_dict[LEG][2].bodyparttree),
                        addedinfo=serialmodule.bodyparts_dict[LEG][2].addedinfo),
                },
            }
            contactrel = serialmodule.contactrel
            xy_crossed = serialmodule.xy_crossed
            xy_linked = serialmodule.xy_linked
            directions = serialmodule.directions

            unserialized[k] = RelationModule(relationx, relationy, bodyparts_dict, contactrel,
                                             xy_crossed, xy_linked, directionslist=directions,
                                             articulators=articulators, timingintervals=timingintervals,
                                             addedinfo=addedinfo)
            unserialized[k].uniqueid = k
        self.relationmodules = unserialized

    # technically this should not be implemented, because Sign objects are mutable
    # but a Corpus is implemented as a set of Sign objects, so we need a hash function
    def __hash__(self):
        # sign hash is based on entryid counter,
        # which is the only identifier that is both obligatory and guaranteed unique
        return hash(self.signlevel_information.entryid.counter)

    # Ref: https://eng.lyft.com/hashing-and-equality-in-python-2ea8c738fb9d
    def __eq__(self, other):
        # sign equality is based on entryid counter,
        # which is the only identifier that is both obligatory and guaranteed unique
        return isinstance(other, Sign) and self.signlevel_information.entryid.counter == other.signlevel_information.entryid.counter

    def __repr__(self):
        glosses_string = glossesdelimiter.join(self.signlevel_information.gloss)
        return '<SIGN: ' + repr(glosses_string) + ' - ' + repr(self.signlevel_information.entryid) + '>'

    @property
    def signlevel_information(self):
        return self._signlevel_information

    @signlevel_information.setter
    def signlevel_information(self, signlevelinfo):
        self._signlevel_information = signlevelinfo  # SignLevelInformation(signlevelinfo)
        self._signlevel_information.parentsign = self

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

    def lastmodifiednow(self):
        self.signlevel_information.lastmodifiednow()

    @property
    def signtype(self):
        return self._signtype

    @signtype.setter
    def signtype(self, stype):
        self._signtype = stype

    @property
    def xslotstructure(self):
        return self._xslotstructure

    @xslotstructure.setter
    def xslotstructure(self, xslotstruct):
        self._xslotstructure = xslotstruct

    def updatemodule(self, existingkey, updated_module, moduletype):
        current_module = self.getmoduledict(moduletype)[existingkey]
        ischanged = False

        currentmod_attrs = current_module.__dict__
        updatedmod_attrs = updated_module.__dict__
        for attr in currentmod_attrs:
            if currentmod_attrs[attr] != updatedmod_attrs[attr]:
                # TODO KV note that locationtreemodel and movementtreemodel don't have __eq__ & __ne__ methods;
                # therefore copies (even if identical) of these classes will not be assessed as equal
                currentmod_attrs[attr] = updatedmod_attrs[attr]
                ischanged = True
        if ischanged:
            self.lastmodifiednow()

    def addmodule(self, module_to_add, moduletype):
        self.getmoduledict(moduletype)[module_to_add.uniqueid] = module_to_add
        self.getmodulenumbersdict(moduletype)[module_to_add.uniqueid] = self.getnextmodulenumber(moduletype)
        self.lastmodifiednow()

    def getnextmodulenumber(self, moduletype):
        modulenumbersdict = self.getmodulenumbersdict(moduletype)
        modulenumberslist = list(modulenumbersdict.values())
        largestnum = max(modulenumberslist) if len(modulenumberslist) > 0 else 0
        return largestnum + 1

    def removemodule(self, uniqueid, moduletype):
        self.getmoduledict(moduletype).pop(uniqueid)
        self.removemodulenumber(uniqueid, moduletype)
        self.lastmodifiednow()

    def removemodulenumber(self, uniqueid, moduletype):
        removedmodulenum = self.getmodulenumbersdict(moduletype).pop(uniqueid)
        modulenumbersdict = self.getmodulenumbersdict(moduletype)
        # renumber modules
        renumberedmodules = {}
        for uid in modulenumbersdict.keys():
            modnum = modulenumbersdict[uid]
            if modnum < removedmodulenum:
                renumberedmodules[uid] = modnum
            else:
                renumberedmodules[uid] = modnum - 1
        for uid in modulenumbersdict.keys():
            self.updatemodulenumber(uid, moduletype, renumberedmodules[uid])

    def updatemodulenumber(self, uniqueid, moduletype, newmodnum):
        self.getmodulenumbersdict(moduletype)[uniqueid] = newmodnum

    def gettimedmodules(self):
        return [self.movementmodules, self.locationmodules, self.relationmodules, self.orientationmodules, self.handconfigmodules]


class Corpus:
    #TODO: need a default for location_definition
    def __init__(self, signs=None, location_definition=None, path=None, serializedcorpus=None, minimumID=1, highestID=0):
        if serializedcorpus:
            self.signs = set([Sign(serializedsign=s) for s in serializedcorpus['signs']])
            # self.location_definition = serializedcorpus['loc defn']
            self.path = serializedcorpus['path']
            self.minimumID = serializedcorpus['minimum id'] if 'minimum id' in serializedcorpus.keys() else 1
            self.highestID = serializedcorpus['highest id']
            # check and make sure the highest ID saved is equivalent to the actual highest entry ID unless the corpus is empty 
            # see issue #242: https://github.com/PhonologicalCorpusTools/SLPAA/issues/242
            if len(self) > 0:
                self.confirmhighestID("load")
            self.add_missing_paths()  # Another backwards compatibility function for movement and location
        else:
            self.signs = signs if signs else set()
            self.location_definition = location_definition
            # self.movement_definition = movement_definition
            self.path = path
            self.minimumID = minimumID
            self.highestID = highestID

    # check and make sure the highest ID saved is equivalent to the actual highest entry ID
    # see issue  # 242: https://github.com/PhonologicalCorpusTools/SLPAA/issues/242
    # this function should hopefully not be necessary forever, but for now I want to make sure that
    # functionality isn't affected by an incorrectly-saved value
    def confirmhighestID(self, actionname):
        entryIDcounters = [s.signlevel_information.entryid.counter for s in self.signs] or [0]
        max_entryID = max(entryIDcounters)
        if max_entryID > self.highestID:
            logging.warn(" upon " + actionname + " - highest entryID was not correct (recorded as " + str(self.highestID) + " but should have been " + str(max_entryID) + ");\nplease copy/paste this warning into an email to Kaili, along with the name of the corpus you're using")
            self.highestID = max_entryID

    def increaseminID(self, newmin):
        if newmin > self.minimumID:
            increase_amount = newmin - self.minimumID
            self.minimumID = newmin
            for s in self.signs:
                s.signlevel_information.entryid.counter += increase_amount
            self.highestID += increase_amount

    def serialize(self):
        # check and make sure the highest ID saved is equivalent to the actual highest entry ID unless the corpus is empty
        # see issue #242: https://github.com/PhonologicalCorpusTools/SLPAA/issues/242
        if len(self) > 0:
            self.confirmhighestID("save")
        return {
            'signs': [s.serialize() for s in list(self.signs)],
            # 'loc defn': self.location_definition,
            'path': self.path,
            'minimum id': self.minimumID,
            'highest id': self.highestID
        }

    def get_all_lemmas(self):
        return [sign.signlevel_information.lemma for sign in self.signs]

    def get_all_idglosses(self):
        return [sign.signlevel_information.idgloss for sign in self.signs]

    def add_sign(self, new_sign):
        self.signs.add(new_sign)
        self.highestID = max(new_sign.signlevel_information.entryid.counter, self.highestID)

    def remove_sign(self, trash_sign):
        self.signs.remove(trash_sign)

    def __contains__(self, item):
        return item in self.signs

    def __iter__(self):
        return iter(self.signs)

    def __len__(self):
        return len(self.signs)

    def __repr__(self):
        filename = "not yet saved"
        if self.path:
            _, filename = os.path.split(self.path)
        return '<CORPUS: ' + repr(filename) + '>'
    
    def add_missing_paths(self):
        for sign in self.signs:
            correctionsdict = {ModuleTypes.MOVEMENT: {},
                               ModuleTypes.LOCATION: {},
                               ModuleTypes.RELATION: {}}
            entryidcounter = sign.signlevel_information.entryid.counter
            for type in [ModuleTypes.MOVEMENT, ModuleTypes.LOCATION, ModuleTypes.RELATION]:
                moduledict = sign.getmoduledict(type)

                for count, k in enumerate(moduledict):
                    correctionsdict[type][entryidcounter] = {}
                    module = moduledict[k]

                    if type == ModuleTypes.MOVEMENT:
                        self.add_missing_paths_helper(entryidcounter, module.movementtreemodel, type, count, correctionsdict)
                    elif type == ModuleTypes.LOCATION:
                        self.add_missing_paths_helper(entryidcounter, module.locationtreemodel, type, count, correctionsdict)
                    elif type == ModuleTypes.RELATION:
                        if module.no_selections():
                            label = "   EntryID counter {:<10} {:<9}".format("   " + str(entryidcounter) + " ", str(type) + str(count + 1))
                            mssg = ": Main module has no selections. Is something missing?"
                            logging.warning(label + mssg)

                        bodyparts_dict = module.bodyparts_dict
                        articulators, numbers = module.get_articulators_in_use()
                        models = []
                        for ctr in range(len(articulators)):
                            models.append(bodyparts_dict[articulators[ctr]][numbers[ctr]].bodyparttreemodel)

                        empty_module_flag = False
                        for m in models:
                            if len(m.get_checked_from_serialized_tree()) == 0:
                                empty_module_flag = True
                            self.add_missing_paths_helper(entryidcounter, m, type, count, correctionsdict, verbose=False)
                        if empty_module_flag and module.contactrel.contact:
                            label = "   EntryID counter {:<10} {:<9}".format("   " + str(entryidcounter) + " ", str(type) + str(count + 1))
                            mssg = ": Module has no bodypart selections. Is something missing?"
                            logging.warning(label + mssg)
                          
    def add_missing_paths_helper(self, entryidcounter, treemodel, type, count, correctionsdict, verbose=True):
        paths_missing_bc = []
        paths_not_found = []

        if verbose and len(treemodel.get_checked_from_serialized_tree()) == 0:
            label = "   EntryID counter {:<10} {:<9}".format("   " + str(entryidcounter) + " ", str(type) + str(count + 1))
            mssg = ": Module has no selections. Is something missing?"
            logging.warning(label + mssg)

        missing_values = treemodel.compare_checked_lists()

        newpaths = []

        for oldpath in missing_values:
            paths_to_add = self.get_paths_to_add(oldpath, type)

            if len(paths_to_add) == 0: 
                paths_missing_bc.append(oldpath)
                label = "   EntryID counter " + str(entryidcounter) + " " + str(type) + str(count+1)
                logging.warning(label+": bad backwards compatibility for " + oldpath)
                
            for path in paths_to_add:
                newpath = treepathdelimiter.join(path)
                correctionsdict[type][entryidcounter][newpath] = oldpath
                newpaths.append(newpath)
        thisdict = correctionsdict[type][entryidcounter]
        treemodel.addcheckedvalues(treemodel.invisibleRootItem(), newpaths, thisdict)
        
        if len(newpaths) != 0:
            for i in newpaths:
                label = "   EntryID counter " + str(entryidcounter) + " " + str(type) + str(count+1)
                logging.warning(label +": bad backwards compatibility for " + i)
                paths_not_found.append(thisdict[i])

        for p in missing_values:
            if p not in paths_missing_bc and p not in paths_not_found:
                treemodel.uncheck_paths_from_serialized_tree(missing_values)
    
        
        return 

    # Converts a string representing a movement/location path into a list of nodes
    def get_node_sequence(self, item):
        nodes = []
        curr = ""
        for c in item:
            if (c is not treepathdelimiter):
                curr = curr + c
            else:
                nodes.append(curr)
                curr = ""
        nodes.append(curr)
        return nodes
    
    def get_paths_to_add(self, path, modtype):
        nodes = self.get_node_sequence(path)
        paths_to_add = []
        length = len(nodes)
        if modtype == ModuleTypes.MOVEMENT:
            # Issue 193: Update thumb movements in joint activity section
            if nodes[0] == 'Joint activity':
                if (length > 1 and nodes[1] == 'Thumb base / metacarpophalangeal'):
                    if (length > 2 and (nodes[2] in ['Abduction', 'Adduction'])):
                        nodes[1] = 'Thumb root / carpometacarpal (CMC)'
                        paths_to_add.append(nodes[0:2] + (['Radial abduction'] if nodes[2] == 'Abduction' else ['Radial adduction']))
                        paths_to_add.append(nodes[0:2] + (['Palmar abduction'] if nodes[2] == 'Abduction' else ['Palmar adduction']))
                    
                    elif (length > 2 and nodes[2] == 'Circumduction'):
                        nodes[1] = 'Thumb root / carpometacarpal (CMC)'
                        paths_to_add.append(nodes)
                        
                    elif (length > 2 and nodes[2] == 'Opposition'):
                        nodes[1] = 'Thumb complex movement'
                        paths_to_add.append(nodes)

                    else: # Flexion/extension
                        nodes[1] = 'Thumb base / metacarpophalangeal (MCP)'
                        paths_to_add.append(nodes)
                    
                elif (length > 1 and nodes[1] == 'Thumb non-base / interphalangeal'):
                    nodes[1] = 'Thumb non-base / interphalangeal (IP)'
                    paths_to_add.append(nodes)
                
            # Fix some minor spelling / punctuation changes from issue #195
            if (length > 2 and nodes[2] == 'Rubbing'):
                if length > 3 and nodes[3] == 'Articulators':
                    nodes[3] = 'Articulator(s):'
                elif length > 3 and nodes[3] == 'Location':
                    nodes[3] = 'Location:'
                elif length > 4 and nodes[3] in ['Across', 'Along']:
                    nodes[4] = nodes[4].lower()
                paths_to_add.append(nodes)
            # Issue 194: Add abs/rel movement options 
            if (length > 2 and nodes[1] == 'Perceptual shape' and nodes[3] in ['Horizontal', 'Vertical', 'Sagittal']):
                nodes.insert(3, 'Absolute')
                paths_to_add.append(nodes)
        else: # LOCATION and RELATION
            # Issue 162: hand changes
            if 'hand' in nodes[0] and length > 1:
                if nodes[0] == 'Other hand':
                    nodes[0] = 'Whole hand'
                if nodes[1] in ['Fingers', 'Thumb']:
                    nodes.insert(1, 'Fingers and thumb')
                elif nodes[1][0:7] == 'Finger ':
                    nodes.insert(1, 'Fingers and thumb')
                    nodes.insert(2, 'Fingers')
                elif nodes[1][0:8] == 'Between ':
                    nodes.insert(1, 'Fingers and thumb')
                    nodes.insert(2, 'Between fingers')
                elif nodes[1] == 'Selected fingers':
                    nodes.insert(1, 'Fingers and thumb')
                    nodes.insert(2, 'Selected fingers and thumb')
                elif nodes[1] == 'Selected fingers and Thumb':
                    nodes[1] = 'Selected fingers and thumb'
                    nodes.insert(1, 'Fingers and thumb')
                paths_to_add.append(nodes)
            # Issue 162: leg and feet changes
            elif nodes[0] == 'Legs and feet':
                nodes[0] = 'Leg and foot'
                paths_to_add.append(nodes)
            # Issue 162: Arm changes
            elif nodes[0] == 'Arm (contralateral)':
                nodes[0] = 'Arm'
                if length == 1:
                    nodes.insert(1, 'Arm - contra')
                elif length == 2:
                    nodes.insert(1, nodes[1]) 
                    nodes[2] = nodes[2] + ' - contra'
                elif length == 3: 
                    nodes.insert(2, nodes[2])
                    nodes[3] = nodes[3] + ' - contra'
                paths_to_add.append(nodes)
            # Issue 162: New torso layers
            elif nodes[0] == 'Torso' and length > 1:
                if nodes[1] in ['Hip', 'Groin', 'Buttocks', 'Pelvis area']:
                    nodes.insert(1, 'Lower torso')
                else:
                    nodes.insert(1, 'Upper torso')
                paths_to_add.append(nodes)
            # Issue 162: New face layers
            elif length > 2 and nodes[0] == 'Head' and nodes[1] == 'Face':
                if nodes[2] in ['Above forehead (hairline)', 'Forehead', 'Temple']:
                    nodes.insert(2, 'Forehead region')
                elif nodes[2] in ['Eyebrow', 'Eye']:
                    nodes.insert(2, 'Eye region')
                elif length > 3 and nodes[3] in ['Upper eyelid', 'Lower eyelid']:
                    nodes.insert(4, 'Eyelid')
                elif nodes[-1] == 'Septum':
                    nodes.insert(length-2, 'Septum/nostril area')
                paths_to_add.append(nodes)
            elif length > 2 and nodes[1] == 'Ear':
                nodes[3].replace('Mastoid process', 'Behind ear')
                paths_to_add.append(nodes)
        return paths_to_add
