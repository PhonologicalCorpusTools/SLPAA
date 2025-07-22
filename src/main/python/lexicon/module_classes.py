from datetime import datetime
from fractions import Fraction
from itertools import chain
import functools
import time, os, re

from PyQt5.QtCore import (
    Qt,
    QSettings
)

from constant import NULL, PREDEFINED_MAP, HAND, ARM, LEG, userdefinedroles as udr, treepathdelimiter, ModuleTypes, \
    SURFACE_SUBAREA_ABBREVS, DEFAULT_LOC_1H, DEFAULT_LOC_2H, TargetTypes, HandConfigSlots, SIGN_TYPE
from constant import (specifytotalcycles_str, numberofreps_str, custom_abbrev)

PREDEFINED_MAP = {handshape.canonical: handshape for handshape in PREDEFINED_MAP.values()}

def get_path_lowest_node(path):
    '''Return the lowest node of a path. 
        e.g. 'Whole hand>Finger 1' returns 'Finger 1'\n
            'Whole hand' returns 'Whole hand'
    '''
    return path.split(treepathdelimiter)[-1]

# Resetting a module's uniqueid can come so quickly on the heels of another
#   (e.g. if copy/pasting several modules that aren't treemodel-based)
#   that they end up getting reassigned the exact same timestamp as uniqueid;
#   this decorator ensures that there is at least a brief pause before reassigning,
#   so that we avoid accidentally duplicate uniqueids
def delay_uniqueid_reset(func):
    @functools.wraps(func)
    def wrapper_delay_uniqueid_reset(self, *args, **kwargs):
        time.sleep(1/1000000)
        func(self, *args, **kwargs)

    return wrapper_delay_uniqueid_reset


# common ancestor for timed parameter modules such as HandConfigurationModule, MovementModule, etc
class ParameterModule:

    def __init__(self, articulators, timingintervals=None, phonlocs=None, addedinfo=None):
        self._articulators = articulators
        self._phonlocs = phonlocs
        self._timingintervals = []
        if timingintervals is not None:
            self.timingintervals = timingintervals
        self._addedinfo = addedinfo if addedinfo is not None else AddedInfo()
        self._uniqueid = datetime.timestamp(datetime.now())
        self._moduletype = ""

    @property
    def moduletype(self):
        if not hasattr(self, '_moduletype'):
            # for backward compatibility with pre-20241018 parameter modules
            self._moduletype = ""
        return self._moduletype

    @moduletype.setter
    def moduletype(self, moduletype):
        # validate the input string
        if moduletype in ModuleTypes.parametertypes:
            self._moduletype = moduletype

    def has_articulators(self):
        """ Between articulator 1 and articulator 2, at least one is True.
        """
        return self.articulators[1][1] or self.articulators[1][2] # 

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

    @delay_uniqueid_reset
    def uniqueid_reset(self):
        self.uniqueid = datetime.timestamp(datetime.now())

    @property
    def timingintervals(self):
        return self._timingintervals

    @timingintervals.setter
    def timingintervals(self, timingintervals):
        self._timingintervals = [t for t in timingintervals]

    def get_art_abbrev(self): # articulator abbreviation
        todisplay = ""
        # self.articulators is (Articulator, {1: bool, 2: bool})
        k = self.articulators[0] # hand, arm, or leg
        if self.articulators[1][1] and not self.articulators[1][2]: # articulator 1
            todisplay = k + " " + str(1)
        elif self.articulators[1][2] and not self.articulators[1][1]: # articulator 2
            todisplay = k + " " + str(2)
        elif self.articulators[1][1] and self.articulators[1][2]: # both articulators
            todisplay = "Both " + k.lower() + "s"
            if self.inphase == 1:
                todisplay += " in phase"
            elif self.inphase == 2:
                todisplay += " out of phase"
            elif self.inphase == 3:
                todisplay += " connected"
            elif self.inphase == 4:
                todisplay += " connected, in phase"
        return todisplay



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
            # backward compatibility for attribute added 20250713
            self._partsofspeech = serializedsignlevelinfo['partsofspeech'] if 'partsofspeech' in serializedsignlevelinfo else ([], "")
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
            # backward compatibility for attribute added 20250713
            self._partsofspeech = signlevel_info['partsofspeech'] if 'partsofspeech' in signlevel_info else ([], "")

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
            'handdominance': self._handdominance,
            'partsofspeech': self._partsofspeech
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
    
    def getabbreviation(self):
        # used in search function. 
        to_append = []
        if self.gloss:
            to_append.append(f"gloss={self.gloss}") # update once search allows multiple glosses
        if self.entryid.display_string():
            to_append.append(f"entryid={self.entryid.display_string()}")

        # Text properties: for now, match exactly. TODO: allow regex or other matching methods?
        for val in ["idgloss", "lemma", "source", "signer", "frequency", "coder", "note"]:
            sli_attr = getattr(self, val)
            if sli_attr:
                to_append.append(f"{val}={sli_attr}")
        # Binary properties. 
        for val in ["fingerspelled", "compoundsign", "handdominance"]:
            sli_attr = getattr(self, val)
            # fingerspelled and compoundsign can be T/F/None; handdominance can be L/R/None
            if sli_attr not in [None, '']:
                to_append.append(f"{val}={sli_attr}")
        # Dates. TODO: allow date ranges?
        for val in ["datecreated", "datelastmodified"]:
            sli_attr = getattr(self, val)
            if sli_attr:
                to_append.append(f"{val}={sli_attr}")
        return "; ".join(to_append)

    @property
    def partsofspeech(self):
        if not hasattr(self, '_partsofspeech'):
            # backward compatibility for attribute added 20250713
            self._partsofspeech = ([], "")  # default value
        return self._partsofspeech
    
    @partsofspeech.setter
    def partsofspeech(self, pos):
        self._partsofspeech = pos


# This module stores the movement information for a particular articulator/s.
# It also stores "Added Info" (estimated, uncertain, etc) characteristics for each selected movement
# as well as for the module overall.
class MovementModule(ParameterModule):
    def __init__(self, movementtreemodel, articulators, timingintervals=None, phonlocs=None, addedinfo=None, inphase=0):
        self._movementtreemodel = movementtreemodel
        self._inphase = inphase    # TODO is "inphase" actually the best name for this attribute?
        super().__init__(articulators, timingintervals=timingintervals, phonlocs=phonlocs, addedinfo=addedinfo)

    @property
    def moduletype(self):
        return super().moduletype or ModuleTypes.MOVEMENT

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
        def refactor_list(strings):
            if not strings:
                return ""
            prefix = os.path.commonprefix(strings)
             # eg factor Hand (across), Hand (away), Hand (to wrist) into Hand (across + away + to wrist)
            if len(strings) > 1 and prefix and '(' in prefix: 
                prefix = prefix[:prefix.find('(')+1] 
                unique_parts = [re.sub(f"^{re.escape(prefix)}", "", s).strip(" ()") for s in strings]
                return f"{prefix}{' + '.join(unique_parts)})"
            else:
                return f"{' + '.join(filter(None, strings))}"
        phonphon_str = self.phonlocs.getabbreviation() if self.phonlocs else ""
        perceptual_info = {
            "Shape": [],
            "Axis direction": [],
            "Plane": [],
        }
        joint_specific_info, handshape_change_str, mvmtchar_info = [], "", []
        axis_other, plane_other = "", ""
        h1h2 = {"Axis direction": "", "Plane": ""}
        rep_info = {"abbrev": "", "num": None, "min": False, "locn": []}
        
        paths = self.movementtreemodel.get_checked_items(only_fully_checked=False, include_details=True)
        leaf_paths = []
        last_path = paths[0] if paths else None
        for path in paths: 
            # we'll mainly work with the leaf nodes, but occasionally we need to access the abbreviations of other nodes as well.
            if last_path["path"] in path["path"]: # this is a child of last_path
                last_path = path
            else:
                leaf_paths.append(last_path)
                last_path = path
        if last_path is not None: leaf_paths.append(last_path) 
        paths_dict = {}
        for d in paths: # convert to dict for quick lookup
            paths_dict[d['path']] = d
        for path in leaf_paths: # each path contains keys "path", "abbrev", "usv"
            path_nodes = path["path"].split(treepathdelimiter)
            # distinguish between None and "". If "", the path shouldn't appear in the abbreviation (eg for "Not relevant")
            abbrev = path["abbrev"] if path["abbrev"] is not None else path_nodes[-1] 
            if len(path_nodes) == 1: return abbrev
            if path_nodes[0] == "Movement type":
                if path_nodes[1] == "Perceptual shape":
                    if path["abbrev"] == custom_abbrev: abbrev = "" 
                    # node[2] is either Shape, Axis direction, or Plane
                    # node[3] is the specified shape or axis or plane
                    if len(path_nodes) >= 3:
                        shape_type = path_nodes[2] 
                        if shape_type == "Shape" and path["usv"] and path_nodes[-1] == "Other":
                            abbrev = path['usv']
                        elif shape_type == "Axis direction" and len(path_nodes) > 4 and path_nodes[4] == "Other":
                            axis_other = paths_dict[treepathdelimiter.join(path_nodes[0:5])]["usv"] + " "
                        elif shape_type == "Plane":
                            if (not plane_other) and len(path_nodes) > 4 and path_nodes[4] == "Other":
                                plane_other = f"{paths_dict[treepathdelimiter.join(path_nodes[0:5])]['usv']} " 
                            if len(path_nodes) > 5 and path_nodes[5] == "Specify top of area:":
                                top = paths_dict[path["path"]]['usv']
                                plane_other += f"(top: {top}) "
                        if abbrev.startswith("H1 & H2"):
                            h1h2[shape_type] = abbrev 
                        else:
                            perceptual_info[shape_type].append(abbrev) 

                elif path_nodes[1] == "Joint-specific movements":
                    # node[2] is movement type, node[3] is direction, so need 3 or 4 nodes depending on whether direction is specified.
                    # except when node[2] is "rubbing", which requires 4 or 5 nodes
                    if len(path_nodes) >= 4 and path_nodes[2] == "Rubbing":
                        if path_nodes[3] not in ['Articulator(s):', 'Location:']:
                            joint_specific_info.append(abbrev)
                    else:
                        if path['usv']: abbrev = path['usv']
                        joint_specific_info.append(abbrev)

                elif path_nodes[1] == "Handshape change":
                    handshape_change_str = abbrev
            elif path_nodes[0] == "Movement characteristics":
                if path_nodes[1] == "Repetition":
                    if len(path_nodes) >= 4 and path_nodes[3] == 'Specify total number of cycles':
                        rep_info['abbrev'] = abbrev
                        rep_info["num"] = paths_dict[treepathdelimiter.join(path_nodes[0:4])]["usv"]
                        if not rep_info["num"]:
                            print("unspecified num reps")
                        if len(path_nodes) == 5: # "this number is a minimum" 
                            rep_info["min"] = True 
                    elif len(path_nodes) >= 6 and path_nodes[3] == 'Location of repetition': # if location is specified, path is at least 6 nodes long
                        rep_info["locn"].append(abbrev)
                    else: # single
                        rep_info['abbrev'] = abbrev


                else: # directionality or additional characteristics
                    # Handle usv options for additional characteristics
                    if path_nodes[-1] != "Relative to":  # ugly, but we handle this usv case separately
                        if path_nodes[1] == "Additional characteristics": 
                            if len(path_nodes) >= 3:
                                if path['usv']: 
                                    parent_abbrev = path_nodes[-2]
                                    abbrev = f"{parent_abbrev}: {path['usv']}"
                                    # abbrev = paths[treepathdelimiter.join(path_nodes[0:-2])] + treepathdelimiter + path['usv']
                                relativeto_path = treepathdelimiter.join(path_nodes[0:3]) + treepathdelimiter + "Relative to"
                                if relativeto_path in paths_dict: # not great but does the trick
                                    abbrev += f" (relative to {paths_dict[relativeto_path]['usv']})"

                        mvmtchar_info.append(abbrev)
            elif len(path_nodes) > 1 and path_nodes[0] == "Joint activity": # TODO eventually
                pass
        
        perceptual_info['Axis direction'] = f"{axis_other}({refactor_list(perceptual_info['Axis direction'])})" if axis_other else refactor_list(perceptual_info['Axis direction'])
        perceptual_info['Plane'] = f"{plane_other}({refactor_list(perceptual_info['Plane'])})" if plane_other else refactor_list(perceptual_info['Plane'])
        perceptual_info_str = '; '.join(filter(None, (['; '.join(filter(None, perceptual_info['Shape'])), h1h2['Axis direction'], perceptual_info['Axis direction'], h1h2['Plane'], perceptual_info['Plane']])))
        
        perceptual_str = None if not perceptual_info_str else f"Perceptual ({perceptual_info_str})" 
        joint_specific_info_str = None if not joint_specific_info else f"Joint-specific ({refactor_list(joint_specific_info)})" 
        if rep_info['abbrev']:
            if not rep_info["num"]: rep_str = rep_info['abbrev']
            else: 
                rep_str = f"{'min ' if rep_info['min'] else ''}{rep_info['num']}x"
                # rep_info['abbrev'] if not rep_info['min'] else f"{'min '}{rep_info['num']}x"
            if rep_info['locn']: rep_str += f" (Different loc: {' + '.join(rep_info['locn'])})"
        else: rep_str = ""
        mvmtchar_str = None if not mvmtchar_info else '; '.join(filter(None, mvmtchar_info))


        to_return = '; '.join(filter(None, [phonphon_str, perceptual_str, joint_specific_info_str, handshape_change_str, rep_str, mvmtchar_str]))
        return to_return
        # return to_return
        


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
    
    def getabbreviation(self):
        if self.allfalse():
            return ""
        to_return = []
        if self.phonologicalloc:
            if self.majorphonloc and not self.minorphonloc:
                to_return.append("maj. phonol")
            elif self.minorphonloc and not self.majorphonloc:
                to_return.append("min. phonol")
            else:
                to_return.append("phonol")
        if self.phoneticloc:
            to_return.append("phonet")
        if self.phonologicalloc and self.phoneticloc:
            return (f"{to_return[0]} and {to_return[1]}").capitalize()
        return to_return[0].capitalize()



        


# this class stores info about what kind of location type (body or signing space)
# is used by a particular instance of the Location Module
class LocationType:

    def __init__(self, body=False, signingspace=False, bodyanchored=False, purelyspatial=False):
        self._body = body
        self._signingspace = signingspace
        self._bodyanchored = bodyanchored
        self._purelyspatial = purelyspatial
    
    def __eq__(self, other):
        return isinstance(other, LocationType) and self.body == other.body and self.signingspace == other.signingspace and self.bodyanchored == other.bodyanchored and self.purelyspatial == other.purelyspatial

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
    
    def getabbreviation(self):
        if self.allfalse():
            return ""
        if self._body:
            return "Body"
        elif self._signingspace:
            if self._bodyanchored:
                return "Signing space(body-anch)"
            elif self._purelyspatial:
                return "Signing space(spatial)"
            return "Signing space"
        return "Other loctype"

# Represents one specific point in time in an x-slot timing structure
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

    # returns True iff this timing point occurs earlier in the x-slot structure than the other
    def __lt__(self, other):
        if isinstance(other, TimingPoint):
            if self._wholepart < other.wholepart:
                return True
            elif self._wholepart == other.wholepart:
                if self._fractionalpart < other.fractionalpart:
                    return True
        return False

    # returns True iff this and the other point are at effectively the same point in time, whether
    #   because they are in fact equal OR because they are adjacent (see function adjacent())
    def equivalent(self, other):
        if isinstance(other, TimingPoint):
            return self.adjacent(other) or self.__eq__(other)

    # returns True iff this and the other point are directly adjacent to one another
    #   for example, if this point is at the end of x1 and the other is at the beginning of x2
    def adjacent(self, other):
        if isinstance(other, TimingPoint):
            if self.fractionalpart == 1 and other.fractionalpart == 0 and (self.wholepart + 1 == other.wholepart):
                return True
            elif other.fractionalpart == 1 and self.fractionalpart == 0 and (other.wholepart + 1 == self.wholepart):
                return True
        return False

    # returns True iff this timing point occurs later in the x-slot structure than the other
    def __gt__(self, other):
        if isinstance(other, TimingPoint):
            return other.__lt__(self)
        return False

    # returns True iff this timing point occurs at the same time or earlier in the x-slot structure vs the other
    def __le__(self, other):
        return not self.__gt__(other)

    # returns True iff this timing point occurs at the same time or later in the x-slot structure vs the other
    def __ge__(self, other):
        return not self.__lt__(other)

    # returns True iff this timing point occurs strictly earlier in the x-slot structure vs the other point or interval
    def before(self, other):
        if isinstance(other, TimingPoint):
            return self.__lt__(other)
        elif isinstance(other, TimingInterval):
            return other.after(self)
        return False

    # returns True iff this timing point occurs strictly later in the x-slot structure vs the other point or interval
    def after(self, other):
        if isinstance(other, TimingPoint):
            return self.__gt__(other)
        elif isinstance(other, TimingInterval):
            return other.before(self)
        return False


# Represents an interval in time (from one TimingPoint to another) in an x-slot timing structure
# In order to represent a "whole sign" timing interval (no matter how many x-slots long), use
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

    # returns the start and end points of the interval as a tuple of (TimingPoint, TimingPoint)
    def points(self):
        return self.startpoint(), self.endpoint()

    # set the value of the interval to the given start and end points
    # startpt and endpt must both be of type TimingPoint
    def setinterval(self, startpt, endpt):
        if not (isinstance(startpt, TimingPoint) and isinstance(endpt, TimingPoint)):
            raise TypeError("Inputs must both be of type TimingPoint.")
        elif startpt <= endpt:
            self._startpoint = startpt
            self._endpoint = endpt
        else:
            raise ValueError("Start point greater than end point.")

    # returns True iff this is a degenerate interval; ie, its beginning and end points are the same
    def ispoint(self):
        return self._startpoint == self._endpoint

    # returns True iff the entirety of this timing interval occurs strictly earlier in the x-slot structure vs the other point or interval
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

    # returns True iff the entirety of this timing interval occurs strictly later in the x-slot structure vs the other point or interval
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

    # returns True iff this interval is directly adjacent to the other
    #   ie, the end point of one is equivalent to the start point of the other
    def adjacent(self, other):
        if isinstance(other, TimingInterval):
            return self.endpoint.equivalent(other.startpoint) or other.endpoint.equivalent(self.startpoint)
        return False

    # returns True iff the start and end points of this and the other interval are equal
    def __eq__(self, other):
        if isinstance(other, TimingInterval):
            return self.startpoint == other.startpoint and self.endpoint == other.endpoint
        return False

    # returns True iff the intersection of this and the other interval is nonempty
    #   and in fact contains more than just, eg, one point of adjacency
    def overlapsinterval(self, other):
        if isinstance(other, TimingInterval):
            if self.iswholesign() or other.iswholesign():
                return True
            # either other starts at or in self, or self starts at or in other
            elif (self.startpoint <= other.startpoint and self.endpoint > other.startpoint) or (other.startpoint <= self.startpoint and other.endpoint > self.startpoint):
                return True
        return False
    
    # returns True iff the other interval is a subset (not necessarily proper) of this one
    def includesinterval(self, other):
        if isinstance(other, TimingInterval):
            if self.iswholesign():
                return True
            elif self.startpoint <= other.startpoint and self.endpoint >= other.endpoint:
                return True
        return False

    # returns True iff this interval covers the entire timing duration of the sign
    def iswholesign(self):
        return self.startpoint == TimingPoint(0, 0) and self.endpoint == TimingPoint(0, 1)

    def __repr__(self):
        return '<TimingInterval: ' + repr(self._startpoint) + ', ' + repr(self._endpoint) + '>'


# This class represents additional information that can be appended to many different types of entries in SLP-AA,
#   such as to an entire module, one selection in a movement module, one surface selection in a location module, etc
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

    # returns True iff this AddedInfo instance has at least flag set or at least one note with non-whitespace text
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
        # backward compatibility for pre-20250529 sign type (with only one articulator and therefore only one AddedInfo)
        self._addedinfo = {HAND: AddedInfo(), ARM: AddedInfo(), LEG: AddedInfo()}
        if addedinfo is not None:
            if isinstance(addedinfo, AddedInfo):
                # if there's just one instead of a dictionary of 3, it was meant for Hand
                addedinfo = {HAND: addedinfo}
            self._addedinfo.update(addedinfo)
        self._moduletype = ModuleTypes.SIGNTYPE

    # == check compares all content (equality does not require references to be to the same spot in memory)
    def __eq__(self, other):
        if isinstance(other, Signtype):
            self_attributes = self.__dict__
            other_attributes = other.__dict__
            return False not in [self_attributes[attr] == other_attributes[attr] for attr in self_attributes.keys()]
        return False

    @property
    def moduletype(self):
        if not hasattr(self, '_moduletype'):
            # for backward compatibility with pre-20241018 sign type
            print("signtype backward compatibility")
            self._moduletype = ModuleTypes.SIGNTYPE
        return self._moduletype

    @property
    def addedinfo(self):
        # backward compatibility for pre-20250529 sign type (with only one articulator and therefore only one AddedInfo)
        if not hasattr(self, '_addedinfo'):
            self._addedinfo = {HAND: AddedInfo(), ARM: AddedInfo(), LEG: AddedInfo()}
        elif isinstance(self._addedinfo, AddedInfo):
            # if there's just one instead of a dictionary of 3, it was meant for Hand
            self._addedinfo = {HAND: self._addedinfo, ARM: AddedInfo(), LEG: AddedInfo()}
        return self._addedinfo

    @addedinfo.setter
    def addedinfo(self, addedinfo):
        # backward compatibility for pre-20250529 sign type (with only one articulator and therefore only one AddedInfo)
        if addedinfo is None or isinstance(self._addedinfo, AddedInfo):
            self._addedinfo = {HAND: AddedInfo(), ARM: AddedInfo(), LEG: AddedInfo()}
        if addedinfo is not None:
            if isinstance(addedinfo, AddedInfo):
                # if there's just one instead of a dictionary of 3, it was meant for Hand
                addedinfo = {HAND: addedinfo}
            self._addedinfo.update(addedinfo)

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
        for spec in self._specslist:
            # include abbreviations for all options
            pathlist = spec.split('.')  # this is the path of abbreviations to this particular setting
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
        # TODO implement
        return "Bodypart abbreviations not yet implemented"


# This module stores the location information for a particular articulator/s.
# It offers the user different location types (on body, in signing space), location options, and
# (for body-referenced locations) specific surfaces and/or subareas.
# It also stores "Added Info" (estimated, uncertain, etc) characteristics for each selected location
# as well as for the module overall.
class LocationModule(ParameterModule):
    def __init__(self, locationtreemodel, articulators, timingintervals=None, phonlocs=None, addedinfo=None, inphase=0):
        self._locationtreemodel = locationtreemodel
        self._inphase = inphase  # TODO is "inphase" actually the best name for this attribute?
        super().__init__(articulators, timingintervals=timingintervals, phonlocs=phonlocs, addedinfo=addedinfo)

    @property
    def moduletype(self):
        return super().moduletype or ModuleTypes.LOCATION

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
        phonphon_str = self.phonlocs.getabbreviation() if self.phonlocs else ""
        loctype_str = self.locationtreemodel.locationtype.getabbreviation()
        is_neutral_str = "neutral" if self.locationtreemodel.defaultneutralselected else ""

        # don't list paths if neutral checkbox is checked or "default neutral space" is a selected path
        if is_neutral_str:
            return ': '.join(filter(None, [phonphon_str, loctype_str, is_neutral_str]))
        
        path_strings = []
        # purely spatial locations don't have surfaces / subareas; we handle the abbrev differently
        if loctype_str == "Signing space(spatial)" and not is_neutral_str:
            # setting only_fully_checked False returns each individual node in the path (eg 'Sagittal axis', 'Sagittal axis>In front)
            # so that we can get the abbreviations of intermediate nodes
            paths = self.locationtreemodel.get_checked_items(only_fully_checked=False, include_details=True) 
            last_node = ""
            curr_abbrev_list = []
            # Each 'curr_node' is a dict. Keys are 'path', 'abbrev', 'details'
            for curr_node in paths:
                if curr_node['path'] == 'Default neutral space':
                    is_neutral_str = "neutral"
                    return ': '.join(filter(None, [phonphon_str, loctype_str, is_neutral_str]))
                else:
                    curr_abbrev = (get_path_lowest_node(curr_node['path']) if curr_node['abbrev'] is None else curr_node['abbrev']).lower()
                    if last_node in curr_node['path']:
                        curr_abbrev_list.append(curr_abbrev)
                    else:
                        # append [ ] if axis / distance is not specified
                        # eg hor[ipsi][ ]; ver[ ][ ]; sag[front][med] 
                        path_strings.append(''.join(curr_abbrev_list) + ''.join(['[ ]' for _ in range(3 - len(curr_abbrev_list))]))
                        curr_abbrev_list = [curr_node['abbrev']]  
                    last_node = curr_node['path']
            if len(curr_abbrev_list) > 0: # in case the list only contains Default neutral space
                path_strings.append(''.join(curr_abbrev_list) + ''.join(['[ ]' for _ in range(3 - len(curr_abbrev_list))]))

        elif loctype_str != "Signing space(spatial)" :
            # each 'path' is a dict. Keys are 'path', 'abbrev', 'details'
            for path in self.locationtreemodel.get_checked_items(include_details=True):
                path_str = get_path_lowest_node(path['path']) if path['abbrev'] is None else path['abbrev']
                # details_dict: keys are the subarea types ('surface', 'sub-area', or ''); 
                # values are lists of checked subareas
                details_dict = path['details'].get_checked_values()
                # add surfaces and subareas in square brackets, eg [ant][centre]; if unspecified, leave square brackets with a space [ ]
                for key, val in details_dict.items(): 
                    if key:
                        path_str += f'[{" " if len(val) == 0 else ", ".join([v if v not in SURFACE_SUBAREA_ABBREVS else SURFACE_SUBAREA_ABBREVS[v] for v in val])}]'
                path_strings.append(path_str)
        path_strings = '; '.join(filter(None, path_strings))
        

        return ': '.join(filter(None, [phonphon_str, loctype_str, is_neutral_str, path_strings]))


class RelationX:

    def __init__(self, h1=False, h2=False, handboth=False, connected=False, arm1=False, arm2=False, armboth=False, leg1=False, leg2=False, legboth=False, other=False, othertext=""):
        self._h1 = h1
        self._h2 = h2
        self._hboth = handboth  # changed 20250220 - used to be self._both
        self._connected = connected
        self._arm1 = arm1
        self._arm2 = arm2
        self._aboth = armboth  # added 20250220
        self._leg1 = leg1
        self._leg2 = leg2
        self._lboth = legboth  # added 20250220
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
            relX_str = "both hands connected"
        elif self.hboth:
            relX_str = "both hands"
        elif self.aboth:
            relX_str = "both arms"
        elif self.lboth:
            relX_str = "both legs"
        elif self.other:
            relX_str = "other"
            if len(self.othertext) > 0:
                relX_str += " (" + self.othertext + ")"
        else:
            rel_dict = self.__dict__
            for attr in rel_dict:
                if attr.endswith((str(1), str(2))) and rel_dict[attr]:
                    relX_str = attr[1:] # attributes are prepended with _
                    break
        return relX_str

    @property
    def h1(self):
        return self._h1

    @h1.setter
    def h1(self, h1):
        if h1:
            self.resetalltoplevelbooleans()
            self._h1 = h1

    @property
    def h2(self):
        return self._h2

    @h2.setter
    def h2(self, h2):
        if h2:
            self.resetalltoplevelbooleans()
            self._h2 = h2

    @property
    def hboth(self):
        if not hasattr(self, '_hboth'):
            # backward compatibility for attribute changed 20250220
            self._hboth = False
            if hasattr(self, '_both'):
                self._hboth = self._both
                del self._both
        return self._hboth

    @hboth.setter
    def hboth(self, hboth):
        if hboth:
            self.resetalltoplevelbooleans()
            self._hboth = hboth

    @property
    def connected(self):
        return self._connected

    @connected.setter
    def connected(self, connected):
        self._connected = connected

        if connected:
            self.hboth = True

    @property
    def arm1(self):
        return self._arm1

    @arm1.setter
    def arm1(self, arm1):
        if arm1:
            self.resetalltoplevelbooleans()
            self._arm1 = arm1

    @property
    def arm2(self):
        return self._arm2

    @arm2.setter
    def arm2(self, arm2):
        if arm2:
            self.resetalltoplevelbooleans()
            self._arm2 = arm2

    @property
    def aboth(self):
        if not hasattr(self, '_aboth'):
            # backward compatibility for attribute added 20250220
            self._aboth = False
        return self._aboth

    @aboth.setter
    def aboth(self, aboth):
        if aboth:
            self.resetalltoplevelbooleans()
            self._aboth = aboth

    @property
    def leg1(self):
        return self._leg1

    @leg1.setter
    def leg1(self, leg1):
        if leg1:
            self.resetalltoplevelbooleans()
            self._leg1 = leg1

    @property
    def leg2(self):
        return self._leg2

    @leg2.setter
    def leg2(self, leg2):
        if leg2:
            self.resetalltoplevelbooleans()
            self._leg2 = leg2

    @property
    def lboth(self):
        if not hasattr(self, '_lboth'):
            # backward compatibility for attribute added 20250220
            self._lboth = False
        return self._lboth

    @lboth.setter
    def lboth(self, lboth):
        if lboth:
            self.resetalltoplevelbooleans()
            self._lboth = lboth

    @property
    def other(self):
        return self._other

    @other.setter
    def other(self, other):
        if other:
            self.resetalltoplevelbooleans()
            self._other = other

    @property
    def othertext(self):
        return self._othertext

    @othertext.setter
    def othertext(self, othertext):
        self._othertext = othertext

    # helper function for all setters, that resets all (main) boolean attributes to False
    def resetalltoplevelbooleans(self):
        self._h1 = False
        self._h2 = False
        self._hboth = False
        self._arm1 = False
        self._arm2 = False
        self._aboth = False
        self._leg1 = False
        self._leg2 = False
        self._lboth = False
        self._other = False

class RelationY:

    def __init__(self, h2=False, arm1=False, arm2=False, armboth=False, leg1=False, leg2=False, legboth=False, existingmodule=False, linkedmoduletype=None, linkedmoduleids=None, other=False, othertext=""):
        self._h2 = h2
        self._arm1 = arm1
        self._arm2 = arm2
        self._aboth = armboth
        self._leg1 = leg1
        self._leg2 = leg2
        self._lboth = legboth
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
        if self.aboth:
            relY_str = "both arms"
        elif self.lboth:
            relY_str = "both legs"
        elif self.existingmodule:
            # print(self.linkedmoduleids)
            relY_str = "existing module"
            if self.linkedmoduletype is not None:
                if self.linkedmoduletype == ModuleTypes.MOVEMENT:
                    relY_str += " (mvmt)"
                else:
                    relY_str += " (locn)"
        elif self.other: 
            relY_str = "other"
            if len(self.othertext) > 0:
                relY_str += " (" + self.othertext + ")"
        else:
            rel_dict = self.__dict__
            for attr in rel_dict:
                if attr.endswith((str(1), str(2))) and rel_dict[attr]:
                    relY_str = attr[1:]  # attributes are prepended with _
                    break
        return relY_str

    @property
    def h2(self):
        return self._h2

    @h2.setter
    def h2(self, h2):
        if h2:
            self.resetallbooleans()
            self._h2 = h2

    @property
    def arm1(self):
        if not hasattr(self, '_arm1'):
            # backward compatibility for attribute added 20250220
            self._arm1 = False
        return self._arm1

    @arm1.setter
    def arm1(self, arm1):
        if arm1:
            self.resetallbooleans()
            self._arm1 = arm1

    @property
    def arm2(self):
        return self._arm2

    @arm2.setter
    def arm2(self, arm2):
        if arm2:
            self.resetallbooleans()
            self._arm2 = arm2

    @property
    def aboth(self):
        if not hasattr(self, '_aboth'):
            # backward compatibility for attribute added 20250220
            self._aboth = False
        return self._aboth

    @aboth.setter
    def aboth(self, aboth):
        if aboth:
            self.resetallbooleans()
            self._aboth = aboth

    @property
    def leg1(self):
        return self._leg1

    @leg1.setter
    def leg1(self, leg1):
        if leg1:
            self.resetallbooleans()
            self._leg1 = leg1

    @property
    def leg2(self):
        return self._leg2

    @leg2.setter
    def leg2(self, leg2):
        if leg2:
            self.resetallbooleans()
            self._leg2 = leg2

    @property
    def lboth(self):
        if not hasattr(self, '_lboth'):
            # backward compatibility for attribute added 20250220
            self._lboth = False
        return self._lboth

    @lboth.setter
    def lboth(self, lboth):
        if lboth:
            self.resetallbooleans()
            self._lboth = lboth

    @property
    def existingmodule(self):
        return self._existingmodule

    @existingmodule.setter
    def existingmodule(self, existingmodule):
        if existingmodule:
            self.resetallbooleans()
            self._existingmodule = existingmodule

    @property
    def linkedmoduletype(self):
        return self._linkedmoduletype

    @linkedmoduletype.setter
    def linkedmoduletype(self, linkedmoduletype):
        if linkedmoduletype in [ModuleTypes.LOCATION, ModuleTypes.MOVEMENT]:
            self._linkedmoduletype = linkedmoduletype
        else:
            raise TypeError("Linked module type must be either LOCATION or MOVEMENT.")

    @property
    def linkedmoduleids(self):
        return self._linkedmoduleids

    @linkedmoduleids.setter
    def linkedmoduleids(self, linkedmoduleids):
        self._linkedmoduleids = linkedmoduleids

    @property
    def other(self):
        return self._other

    @other.setter
    def other(self, other):
        if other:
            self.resetallbooleans()
            self._other = other

    @property
    def othertext(self):
        return self._othertext

    @othertext.setter
    def othertext(self, othertext):
        self._othertext = othertext

    # helper function for all setters, that resets all boolean attributes to False
    def resetalltoplevelbooleans(self):
        self._h2 = False
        self._arm1 = False
        self._arm2 = False
        self._aboth = False
        self._leg1 = False
        self._leg2 = False
        self._lboth = False
        self._existingmodule = False
        self._other = False


class RelationModule(ParameterModule):

    def __init__(self, relationx, relationy, bodyparts_dict, contactrel, xy_crossed, xy_linked, directionslist, articulators, timingintervals=None, phonlocs=None, addedinfo=None):
        self._relationx = relationx or RelationX()
        self._relationy = relationy or RelationY()
        self._bodyparts_dict = {}
        for bodypart in bodyparts_dict:
            if bodypart not in self._bodyparts_dict:
                self._bodyparts_dict[bodypart] = {}
            for n in bodyparts_dict[bodypart]:
                self._bodyparts_dict[bodypart][n] = bodyparts_dict[bodypart][n] or BodypartInfo(bodyparttype=bodypart, bodyparttreemodel=None)
        self._contactrel = contactrel or ContactRelation()
        # backwards compatibility for generic distance axis (issue 387)
        if len(self._contactrel.distances) == 3:
            self._contactrel.distances.append(Distance(axis=Direction.GENERIC))
        self._xy_crossed = xy_crossed
        self._xy_linked = xy_linked
        self._directions = directionslist or [
            Direction(axis=Direction.HORIZONTAL),
            Direction(axis=Direction.VERTICAL),
            Direction(axis=Direction.SAGITTAL),
        ]
        super().__init__(articulators, timingintervals=timingintervals, phonlocs=phonlocs, addedinfo=addedinfo)

    @property
    def moduletype(self):
        return super().moduletype or ModuleTypes.RELATION

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

    def get_treemodel_from_articulator_label(self, label):
        """
        Returns self.bodyparts_dict[articulator][number].bodyparttreemodel,
        where articulator and number are extracted from a string such as "hand1" or "H1"
        """
        number = 1 if label.endswith("1") else 2
        art = ""
        if label.startswith(("h", "H")): 
            art = HAND
        elif label.startswith(("a", "A")):
            art = ARM
        elif label.startswith(("l", "L")):
            art = LEG

        return(self.bodyparts_dict[art][number].bodyparttreemodel)
    
    def get_paths(self, only_fully_checked=True):
        """
        Returns a dict mapping articulators to their selected path details.

        Returns:
            dict:
                - Keys (str): Articulators ('H1', 'H2', 'Arm1', 'Arm2', 'Leg1', 'Leg2').
                - Values (list[dict]): Lists of dictionaries (output from treemodel.get_checked_items())
                    - 'path': the full path
                    - 'abbrev': The abbreviation. None if the path leaf should not be abbreviated
                    - 'details': The details table.
        """
        paths = {}
        arts, nums = self.get_articulators_in_use()
        for i in range(len(arts)):
            label = arts[i] if arts[i] != 'Hand' else 'H'
            bodypartinfo = self.bodyparts_dict[arts[i]][nums[i]]
            treemodel = bodypartinfo.bodyparttreemodel
            paths.update({label + str(nums[i]) : treemodel.get_checked_items(only_fully_checked=only_fully_checked, include_details=True)})
        
        return paths
    
    def get_path_abbrev(self, paths, art): # abbreviation for paths and details tables
        path_strings = []
        for path in paths[art]:
            path_str = get_path_lowest_node(path['path']) if path['abbrev'] is None else path['abbrev']
            details_dict = path['details'].get_checked_values()
            for val in details_dict.values(): # list of surfaces, list of subareas/handjoints
                path_str += f'[{" " if len(val) == 0 else ", ".join([v if v not in SURFACE_SUBAREA_ABBREVS else SURFACE_SUBAREA_ABBREVS[v] for v in val])}]'
            path_strings.append(path_str)
        return f'{art}[{" " if len(path_strings) == 0 else ", ".join(path_strings)}]'

    def has_any_distance(self):
        for dis in self.contactrel.distances:
            if dis.has_selection():
                return True
        return False

    
    def has_any_direction(self): # returns true if anything in direction is selected, including axis checkboxes or crossed/linked
        if self.xy_crossed or self.xy_linked:
            return True
        if self.has_any_direction_axis():
            return True
        return False

    def has_any_direction_axis(self): # returns true if any direction checkbox is selected
        for dir in self.directions:
            if dir.axisselected:
                return True
        return False

    
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
    
    def get_articulators_in_use(self, as_string=False):
        a = []
        n = []
        for b in [HAND, ARM, LEG]:
            for i in [1,2]:
                if self.usesarticulator(b,i):
                    a.append(b)
                    n.append(i)
        if as_string:
            labels = []
            for i in range(len(a)):
                label = a[i] if a[i] != 'Hand' else 'H'
                label += str(n[i])
                labels.append(label)
            return labels
        else:
            return a, n

    def hands_in_use(self):
        return {
            1: self.relationx.hboth or self.relationx.h1,
            2: self.relationx.hboth or self.relationx.h2 or self.relationy.h2
        }

    def arms_in_use(self):
        return {
            1: self.relationx.aboth or self.relationy.aboth or self.relationx.arm1 or self.relationy.arm1,
            2: self.relationx.aboth or self.relationy.aboth or self.relationx.arm2 or self.relationy.arm2
        }

    def legs_in_use(self):
        return {
            1: self.relationx.lboth or self.relationy.lboth or self.relationx.leg1 or self.relationy.leg1,
            2: self.relationx.lboth or self.relationy.lboth or self.relationx.leg2 or self.relationy.leg2
        }

    # relation abbreviation
    def getabbreviation(self):
        phonphon_str = self.phonlocs.getabbreviation() if self.phonlocs else ""

        X_str, Y_str = '', ''
        
        paths = self.get_paths() 

        X_art = self.relationx.displaystr().capitalize()
        if "both" in X_art.lower():
            art1, art2 = ('H1', 'H2') if "hands" in X_art else (('Arm1', 'Arm2') if "arms" in X_art else ('Leg1', 'Leg2'))
            X_str += f'{X_art}: '
            X_str += ', '.join([self.get_path_abbrev(paths, a) for a in [art1, art2]])
        elif X_art.startswith('Other'):
            X_str += X_art
        elif paths and X_art:
            X_str += self.get_path_abbrev(paths, X_art)

        if self.relationy.existingmodule:
            Y_str = f'linked {self.relationy.linkedmoduletype} module'
        else:
            Y_art = self.relationy.displaystr().capitalize()
            if "both" in Y_art.lower():
                art1, art2 = ('H1', 'H2') if "hands" in Y_art else (('Arm1', 'Arm2') if "arms" in Y_art else ('Leg1', 'Leg2'))
                Y_str += f'{Y_art}: '
                Y_str += ', '.join([self.get_path_abbrev(paths, a) for a in [art1, art2]])
            elif Y_art.startswith('Other'):
                Y_str += Y_art
            elif paths and Y_art:
                Y_str = self.get_path_abbrev(paths, Y_art)
        if X_str:
            X_str = "X = " + X_str
        if Y_str:
            Y_str = "Y = " + Y_str

        contact, link_cross_label, relative_label = "", "", ""
        if self.contactrel.contact == False: # if None, then no contact has been specified.
            contact = "No contact"
        elif self.contactrel.contact:
            contacttype, contactmanner = "", ""
            # contact type
            if self.contactrel.has_contacttype:
                if self.contactrel.contacttype.light:
                    contacttype += "light"
                elif self.contactrel.contacttype.firm:
                    contacttype += "firm"
                elif self.contactrel.contacttype.other:
                    contacttype += "other"
                    if len(self.contactrel.contacttype.othertext) > 0:
                        contacttype += f" ({self.contactrel.contacttype.othertext})"
            # contact manner
            if self.contactrel.has_manner:
                if self.contactrel.manner.holding:
                    contactmanner += "holding"
                elif self.contactrel.manner.continuous:
                    contactmanner += "continuous"
                elif self.contactrel.manner.intermittent:
                    contactmanner += "intermittent"
            # create full contact, manner, type string
            to_append = f" ({'; '.join(filter(None, [contacttype, contactmanner]))})" if contacttype or contactmanner else ""
            contact = "Contact" + to_append

        if self.xy_linked or self.xy_crossed:
            linked = "linked" if self.xy_linked else ""
            crossed = "crossed" if self.xy_crossed else ""
            link_cross_label += f"X/Y {', '.join(filter(None, [linked, crossed]))}"

        # direction, distance
        any_dir_dist = []
        any_dir_dist_label = ""
        dir_abbrev, dist_abbrev = "", ""
        dirs, dists = ["", "", ""], ["", "", "", ""] # distance has Generic option
        if len(self.directions) == 1:
            any_dir_dist.append("any direction")
        elif self.has_any_direction_axis(): 
            for i, label in enumerate(["Hor", "Ver", "Sag"]):
                dir_abbrev = self.directions[i].getabbreviation() 
                dirs[i] = f"[{dir_abbrev}]" if dir_abbrev else ""
        if len(self.contactrel.distances) == 1:
            any_dir_dist.append("any distance")
        elif self.has_any_distance():
            for i, label in enumerate(["Hor", "Ver", "Sag", "Gen"]):
                dist_abbrev = self.contactrel.distances[i].getabbreviation() 
                dists[i] = f"[{dist_abbrev}]" if dist_abbrev else ""
        if any_dir_dist:
            any_dir_dist_label = f"{', '.join(filter(None, any_dir_dist))} between X and Y"
        to_append = []
        for i, label in enumerate(["Hor", "Ver", "Sag"]):
            if dirs[i] or dists[i]:
                to_append.append(f"{label} {''.join(filter(None, [dirs[i], dists[i]]))}")
        # if a generic distance is specified
        if len(self.contactrel.distances) > 1:
            generic_dist_label = f"Gen [{self.contactrel.distances[3].getabbreviation()}]" if self.contactrel.distances[3].getabbreviation() else ""
            if generic_dist_label:
                to_append.append(generic_dist_label)
        if to_append:
            relative_label += f"X is {', '.join(filter(None, to_append))} to Y"
        
        return ": ".join(filter(None, [phonphon_str, "; ".join(filter(None, [X_str, Y_str, contact, link_cross_label, any_dir_dist_label, relative_label]))]))
    



class MannerRelation:
    def __init__(self, holding=False, continuous=False, intermittent=False, any=False):
        self._holding = holding
        self._continuous = continuous
        self._intermittent = intermittent
        self._any = any

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

    @property
    def any(self):
        if not hasattr(self, '_any'):
            # for backward compatibility with pre-20241205 relation modules
            self._any = False
        return self._any

    @any.setter
    def any(self, any):
        self._any = any


class ContactRelation:
    def __init__(self, contact=None, contacttype=None, mannerrel=None, distance_list=None):
        self._contact = contact
        self._contacttype = contacttype
        self._manner = mannerrel
        self._distances = distance_list or [
            Distance(Direction.HORIZONTAL),
            Distance(Direction.VERTICAL),
            Distance(Direction.SAGITTAL),
            Distance(Direction.GENERIC)
        ]
        if len(self._distances) == 3:
            self._distances.append(Distance(Direction.GENERIC))

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
                distance_str_list = [repr(axis_dist) for axis_dist in self._distances]
                repr_str += ", ".join([""] + distance_str_list)

        return '<ContactRelation: ' + repr(repr_str) + '>'

    def has_manner(self):
        if self.manner is not None:
            return self.manner.holding or self.manner.intermittent or self.manner.continuous
        return False

    def has_contacttype(self):
        if self.contacttype is not None:
            return self.contacttype.light or self.contacttype.firm or self.contacttype.other
        return False
    
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
    def __init__(self, light=False, firm=False, other=False, othertext="", any=False):
        self._light = light
        self._firm = firm
        self._other = other
        self._othertext = othertext
        self._any = any # Used by search targets to match any contact type selection

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

    @property
    def any(self):
        if not hasattr(self, '_any'):
            # for backward compatibility with pre-20241205 relation modules
            self._any = False
        return self._any

    @any.setter
    def any(self, any):
        self._any = any


# This class is used by the Relation Module to track the axis on which to measure the relation between
# two elements (X and Y), as well as the direction of X relative to Y.
class Direction:
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    SAGITTAL = "sagittal"
    GENERIC = "generic"

    def __init__(self, axis, axisselected=False, plus=False, minus=False, inline=False, any=False):
        self._axis = axis
        self._axisselected = axisselected
        self._plus = plus  # ipsi for horizontal, above for vertical, proximal for sagittal
        self._minus = minus  # contra for horizontal, below for vertical, distal for sagittal
        self._inline = inline  # in line with (for all axes)
        # Used by search targets to match any specified direction. 
        # If axis is None, then match any direction selection (crossed / linked / hor / ver / sag). If axis is selected, then the axis checkbox is checked (hor/ver/sag).
        self._any = any 

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
            plus_label = "proximal"
            minus_label = "distal"

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
    def any(self):
        if not hasattr(self, '_any'):
            # for backward compatibility with pre-20241205 relation modules
            self._any = False
        return self._any

    @any.setter
    def any(self, any):
        self._any = any

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
    
    def has_subselection(self):
        return self.plus or self.minus or self.inline
    
    def getabbreviation(self, sourcemodule=None):
        # returns the abbreviated label of the selected direction depending on this Direction's axis
        # abbreviations might differ depending on the source module, e.g. for Relation we use above/below but for Orientation we use up/down
        vert_plus = "up" if sourcemodule == ModuleTypes.ORIENTATION else "above"
        vert_minus = "down" if sourcemodule == ModuleTypes.ORIENTATION else "below"

        if self.axis == Direction.HORIZONTAL:
            return "ipsi" if self.plus else "contra" if self.minus else "in line" if self.inline else "any" if self.axisselected else ""
        elif self.axis == Direction.VERTICAL:
            return vert_plus if self.plus else vert_minus if self.minus else "in line" if self.inline else "any" if self.axisselected else ""
        elif self.axis == Direction.SAGITTAL:
            return "prox" if self.plus else "dist" if self.minus else "in line" if self.inline else "any" if self.axisselected else ""






# This class is used by the Relation Module to track the axis on which to measure the relation between
# two elements (X and Y), as well as the relative distance between those two elements.
class Distance:

    def __init__(self, axis, close=False, medium=False, far=False, any=False):
        self._axis = axis
        self._close = close
        self._medium = medium
        self._far = far
        # Used by search targets to match any specified distance. 
        # If axis is None, then "any distance between X and Y" is checked. If axis is selected, then the axis checkbox is checked.
        self._any = any 

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

    @property
    def any(self):
        if not hasattr(self, '_any'):
            # for backward compatibility with pre-20241205 relation modules
            self._any = False
        return self._any

    @any.setter
    def any(self, any):
        self._any = any

    def __repr__(self):
        repr_str = self._axis
        if self._close:
            repr_str += " / " + "close"
        elif self._medium:
            repr_str += " / " + "medium"
        elif self._far:
            repr_str += " / " + "far"
        else:
            repr_str += " unselected"

        return '<Distance: ' + repr(repr_str) + '>'

    def getabbreviation(self):
        # returns the abbreviated label of the selected distance 
        return "close" if self.close else "med" if self.medium else "far" if self.far else "any" if self.any else "" 


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
    def moduletype(self):
        return super().moduletype or ModuleTypes.ORIENTATION

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
        phonphon_str = self.phonlocs.getabbreviation() if self.phonlocs else ""
        palm_arr, root_arr = [], []
        
        for i, label in enumerate(["Hor", "Ver", "Sag"]):
            if self.palm[i].axisselected:
                palm_abbrev = label
                dir_abbrev = self.palm[i].getabbreviation(sourcemodule = ModuleTypes.ORIENTATION)
                palm_abbrev += f" ({dir_abbrev})" if dir_abbrev else ""
                palm_arr.append(palm_abbrev)
            if self.root[i].axisselected:
                root_abbrev = label
                dir_abbrev = self.root[i].getabbreviation(sourcemodule = ModuleTypes.ORIENTATION)
                root_abbrev += f" ({dir_abbrev})" if dir_abbrev else ""
                root_arr.append(root_abbrev)
        
        palm_str = f"Palm direction: {' & '.join(palm_arr)}" if palm_arr else ""
        root_str = f"Finger direction: {' & '.join(root_arr)}" if root_arr else ""
        return ': '.join(filter(None, [phonphon_str, '; '.join(filter(None, [palm_str, root_str]))]))


        

# This module is only used in the search window. 
# Used instead of the usual HandConfigurationModule when the user wants to do an extended-fingers search.
class ExtendedFingersModule(ParameterModule):
    def __init__(self, i_extended, finger_selections, num_extended_selections, articulators, timingintervals=None, phonlocs=None, addedinfo=None):
        self._i_extended = i_extended
        self._finger_selections = finger_selections
        self._num_extended_selections = num_extended_selections
        super().__init__(articulators, timingintervals=timingintervals, phonlocs=phonlocs, addedinfo=addedinfo)
    
    @property
    def moduletype(self):
        return super().moduletype or TargetTypes.EXTENDEDFINGERS

    @property
    def i_extended(self):
        return self._i_extended

    @i_extended.setter
    def i_extended(self, value):
        self._i_extended = value

    @property
    def finger_selections(self):
        return self._finger_selections

    @finger_selections.setter
    def finger_selections(self, value):
        self._finger_selections = value

    @property
    def num_extended_selections(self):
        return self._num_extended_selections

    @num_extended_selections.setter
    def num_extended_selections(self, value):
        self._num_extended_selections = value

    # TODO
    def getabbreviation(self):
        return ""

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
    def moduletype(self):
        return super().moduletype or ModuleTypes.HANDCONFIG

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
    
    def config_tuple(self):
        return tuple(HandConfigurationHand(self.handconfiguration).get_hand_transcription_list())

    def thumb_is_unopposed(self, config_tuple):
        if config_tuple[HandConfigSlots.THUMB_OPPOSITION] in ['L', 'U']:
            return True
        return False
        
    def finger_is_extended(self, config_tuple, extended_symbols, finger):
        if finger == 0: # thumb
            if not self.thumb_is_unopposed(config_tuple):
                return False
        if config_tuple[HandConfigSlots.MCP[finger]] in extended_symbols:
            return True
        return False



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

    @property
    def moduletype(self):
        return super().moduletype or ModuleTypes.NONMANUAL


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

    def __eq__(self, other):
        if isinstance(other, XslotStructure):
            return self.number == other.number \
                and self.additionalfraction == other.additionalfraction \
                and set(self.fractionalpoints) == set(other.fractionalpoints)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

