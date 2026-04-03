import argparse, json, traceback
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta
from lexicon.lexicon_classes import Sign, Corpus, unserializelocationmodules, unserializemovementmodules, unserializerelationmodules 
from serialization_classes import renamed_load
from constant import ModuleTypes
import logging
logging.disable(logging.WARNING)

"""Specify where to write logs"""
CONST_OUTPUT_LOG = "/home/grace/Projects/SLPAA/2026.04.02_update_outputlog.txt"

""" Specify the source of .slpaa files. 
Options are: 
- a list of paths
- a single path
- a single directory
"""

CONST_CORPUS_SOURCE = "/home/grace/Projects/SLPAA/CD-ASL/"
# CONST_CORPUS_SOURCE = "/home/grace/Projects/SLPAA/class.slpaa"

""" Specify output path or None. If the file doesn't exist, it will be created. Can be the same as CONST_EXISTING_JSONL_PATH. """
CONST_NEW_JSONL_PATH = "/home/grace/Projects/SLPAA/2026.04.02_fulltest.jsonl"
# CONST_NEW_JSONL_PATH = "/home/grace/Projects/SLPAA/test.jsonl"

""" Specify existing JSONL filepath, or None. """
CONST_EXISTING_JSONL_PATH = "/home/grace/Projects/SLPAA/2026.04.02_fulltest.jsonl"

""" What do you want to do?
Options are:
- "new": 
    everything will be exported to a new file at OUTPUT_PATH. 
    If there is already a file at OUTPUT_PATH, it will be overwritten!!!
- "append all": 
    everything will be appended to the file at EXISTING_JSONL_PATH. 
    If the file doesn't exist, it will be created.
- "append new": 
    only new signs will be appended to the file at EXISTING_JSONL_PATH. 
    A sign is new if its combination of corpus path, sign lemma, and entry id are new.
- "update":
    append new signs and replace updated signs.
    A sign will be updated if its combination of corpus path, sign lemma, and entry id are present but its last modified date has changed.
- "update custom":
    append new signs and replace based on some custom defined function
"""
CONST_EXPORT_OPTION = "update"

logs = []
def log_msg(msg, verbose = False):
    logs.append(msg)
    if verbose: 
        print(msg)


def get_id_from_sign_obj(sign: Sign):
    id = (sign._signlevel_information._entryid.counter, sign._signlevel_information.lemma)
    return id


def write_jsonl_to_file(jsonarr, outfile, option, verbose=False):
    # option is 'a' for append or 'w' for overwrite
    counter = 0
    with open(outfile, option, encoding='utf-8') as f:
        for entry in jsonarr:
            json.dump(entry, f)
            f.write('\n')
            counter += 1
    log_msg(f"Successfully {"wrote" if option == 'w' else "appended" if option == 'a' else ""} {counter} signs to {outfile}", verbose)
        
def map_to_id(jsonarr):
    # return a dict that maps from (lemma, entryid, corpus) values to indices of jsonarr
    # e.g. spec = {"lemma": "TEA", "entryid": 9, "corpus source": "tea.slpaa"} 
    mapping = {}
    for i, sign_dict in enumerate(jsonarr):
        id = (sign_dict["entryid"], sign_dict["lemma"], sign_dict["corpus source"])
        if id in mapping:
            raise Exception(f"json file has a duplicate {id}")
        else:
            mapping[id] = i
    return mapping

def get_corpus_paths(source):    
    # return a list of Paths
    if isinstance(source, list):
        return [Path(f) for f in source]
    else:
        source_path = Path(source)
        if source_path.is_dir():
            return list(Path(source_path).glob("*.slpaa"))
        else:
            return [Path(source)]

def load_jsonarr_from_path(path):
    with open(path, 'r') as f:
        jsonarr = json.load(f)
    return jsonarr

def load_jsonl_from_path(path, verbose=False):
    # also returns a map from sign id to index in jsonarr and modified date
    mapping = {}
    jsonarr = []
    counter = 0
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                sign_dict = json.loads(line)
            except json.JSONDecodeError as e:
                msg = f"Error decoding JSON on line: {line.strip()[0:30]}.... Error: {e}"
                log_msg(msg)
                print(msg)
            else:
                id = (sign_dict["entryid"], sign_dict["lemma"], sign_dict["corpus source"])
                jsonarr.append(sign_dict)
                if id in mapping:
                    msg = f"warning: skipped duplicate {id} in {path}"
                    log_msg(msg)
                    print(msg)
                else:
                    mapping[id] = {"index": counter, "modified": datetime.strptime(sign_dict['date last modified'], '%Y-%m-%d %I:%M:%S%p')}
            counter += 1
    log_msg(f"Loaded {len(mapping)} out of {counter} signs from {path}.", verbose)

    return jsonarr, mapping


def load_corpus_binary(path, corpus_dir = None, as_dict = False, verbose=False):
    # as_dict = True: loads as a dict with (lemma, entryid) as keys and sign objects as values, for quick lookup
    if corpus_dir:
        path = Path(corpus_dir) / path
    
    
    with open(path, 'rb') as f:
        corpus = Corpus(serializedcorpus=renamed_load(f))
        # in case we're loading a corpus that was originally created on a different machine / in a different folder
        corpus.path = path
        log_msg(f"Loaded corpus binary {path} containing {len(corpus.signs)} signs.", verbose)

    if as_dict:
        corpus_dict = {}
        for sign in corpus:
            id = (sign._signlevel_information._entryid.counter, sign._signlevel_information.lemma)
            corpus_dict[id] = sign
        return corpus_dict
    else:
        return corpus

def load_corpus_info(corpus_path, verbose=False):
    # doesn't do backwards compatibility
    with open(corpus_path, 'rb') as f:
        serializedcorpus=renamed_load(f)
    corpus_dict = {}
    for s in serializedcorpus['signs']:
        
        slinfo = s['signlevel'] 
        sign_id = (slinfo['entryid'], slinfo['lemma'])
        corpus_dict[sign_id] = {
            "serialized sign": s,
            "modified": datetime.fromtimestamp(slinfo['date last modified']) 
        }
        # sli["date last modified"] = self._signlevel_information.datelastmodified.strftime()
        
    return corpus_dict



def update_specific_module(moduletype, jsonarr, corpus_dir='/home/grace/Projects/SLPAA/'):
    corp_name = jsonarr[0]['corpus source']
    corp_dict = load_corpus_binary(corp_name, corpus_dir, as_dict=True)
    print(corp_name)
    
    new_arr = []
    for sign_dict in jsonarr:
        if sign_dict['corpus source'] != corp_name:
            corp_dict = load_corpus_binary(corp_name, corpus_dir, as_dict=True)
            print(corp_name)
        id = (sign_dict['entryid'], sign_dict['lemma'])
        print(id)
        try:
            sign_obj = corp_dict[id]
        except:
            print("couldn't find in corpus: ", id)
        to_update = sign_obj.get_module_info(moduletype)
        sign_dict.update(to_update)
        new_arr.append(sign_dict)
    return new_arr

def get_sign_representation(sign: Sign, corpus_name, verbose=False):
    try:
        sign_rep = sign.full_info()
    except Exception:
        msg = traceback.format_exc()
        logs.append(msg, True)
        return None
    else:
        sign_rep["corpus source"] = corpus_name
        return sign_rep
    

def get_corpus_representation(corpus: Corpus, corpus_name, verbose=False):
    signlist = []
    for sign in corpus.signs:
        sign_rep = get_sign_representation(sign, corpus_name, verbose)
        if sign_rep:
            signlist.append(sign_rep)
        else:
            sign_id = get_id_from_sign_obj(sign)
            log_msg(f"Couldn't add {sign_id} from {corpus_name}. Skipped.", verbose)
    return signlist

            
# TODO: eventually these should be incorporated into the as_dict() functions in module_classes or lexicon_classes, but for now just do them after the fact
# horrible

def get_timing_intervals(module, num_xslots):
    intervals, points = [], []
    if module["timing type"] == "whole sign": 
        return ["whole sign"], points
    elif module["timing type"] == "interval" and module["timing intervals"] == [[[1, "start"],[num_xslots, "end"]]]:
        return ["whole sign"], points
    else:
        intervals = [tuple(val for pt in interval for val in pt) for interval in module["timing intervals"]] if module["timing type"] in ["interval", "mixed"] else []
        try:
            points = [tuple(interval) for interval in module["timing points"]] if module["timing type"] in ["point", "mixed"] else []
        except:
            
            print("point thing?", module) # a few movements have point specifications, just ignore
            return intervals, [tuple()]

        return intervals, points



def get_timing_intervals_str(module, num_xslots):
    intervals = ""
    if module["timing type"] == "whole sign": 
        return "whole sign"
    elif module["timing type"] == "interval" and module["timing intervals"] == [[[1, "start"],[num_xslots, "end"]]]:
        return "whole sign"
    else:
        intervals = []
        if module["timing type"] in ["interval", "mixed"]:
            for iv in module["timing intervals"]:
                intervals.append(f"{iv[0][0]}@{iv[0][1]}-{iv[1][0]}@{iv[1][1]}")
        if module["timing type"] in ["point", "mixed"]:
            if "timing points" not in module:
                print("point specification issue", module)
            else:
                for pt in module["timing points"]:
                    intervals.append(f"{pt[0]}@{pt[1]}")

        return " & ".join(intervals)
    
def locn_abbrev(locdetails):
    # locdetails is like {"Whole hand": {"Surface": ["fr"], "Sub-area": []}
    path_str = ""
    if not locdetails:
        return path_str
    for loc, details in locdetails.items():
        path_str = loc
        for label, subarr in details.items():
            path_str += f'[{" " if len(subarr) == 0 else ", ".join(subarr)}]'
    return path_str

def get_loc_str(mod):
    if mod["is neutral?"]:
        return "neutral"
    elif mod["loctype"] != "spatial":
        
        return ", ".join([l.split(">")[-1] for l in mod["locations"]])
    else:
        specs = []
        for dets in mod["locations"].values():
            spec = dets["side"]
            if dets["dist"] not in ["_NA", "_NS"]:
                spec += f"@{dets["dist"]}"
            specs.append(spec)
        return "+".join(specs)
            

def get_hands_str(mod):
    if "hands" in mod:
        return "&".join(mod["hands"])
    elif "articulators" in mod:
        return "&".join(mod["articulators"])


    
def assign_assoc_loc_str(sign, rel_mod):
    assoc_mod_labels = []
    if rel_mod["link type"] in ["movement", "location"]:
        try:
            assoc_mods = sign["assoc rel map"][rel_mod["module number"]]
        except:
            print(sign["assoc rel map"])
            print(sign)
        
        for loc_label, details in sign["location modules"].items():
            if details["module number"] in assoc_mods:
                assoc_mod_labels.append(loc_label)  
        if rel_mod["link type"] == "movement":
            print("relation has linked mvmt")
    elif rel_mod["link type"] == None:
        print("relation has no link type", sign["gloss"], sign["corpus source"])
    rel_mod["linked Y(s)"] = assoc_mod_labels
    return rel_mod
    # for mov_label, details in sign["movement modules"].items():
    #     if details["module number"] == assoc_mod:
    #         rel_mod["assoc mvmts"].append(mov_label)

    

def create_timing_map(sign):
    timing_map = {}
    categories = ["perceptual movements", "joint-specific movements", "handshape change movements"]
    num_xslots = sign["number of xslots"]
    for cat in categories:
        module_map = defaultdict(list)
        for i, mod in enumerate(sign[cat]):
            modints, _ = get_timing_intervals(mod, num_xslots)
            for modint in modints:
                module_map[modint].append(i)
        timing_map[cat] = module_map
    for cat in ["hand config modules", "location modules", "relation modules"]:
        module_map_int = defaultdict(list)
        module_map_pt = defaultdict(list)
        for i, mod in enumerate(sign[cat]):
            modints, modpts = get_timing_intervals(mod, num_xslots)
            for modint in modints:
                module_map_int[modint].append(i)
            for modpt in modpts:
                module_map_pt[modpt].append(i)
        timing_map[cat] = module_map_int
        timing_map[f"{cat} points"] = module_map_pt
          
    return timing_map



def map_by(s, feat):
    mapping = {}
    
    for i,mod in enumerate(s[feat]):  
        timing_str = get_timing_intervals_str(mod, s["number of xslots"])

        hands = get_hands_str(mod)
        if feat == "perceptual movements":
           
            shape = mod["movement details"]["shape"]
            axis_spec = mod["movement details"]["axis specification"]
            axis_spec = "no axis" if isinstance(axis_spec, str) else "+".join(mod["movement details"]["axis specification"].values())
            plane_spec = mod["movement details"]["plane specification"]
            if isinstance(plane_spec, str):
                plane_spec = "no plane" 
            else:
                plane_spec = "+".join(mod["movement details"]["plane specification"].values())
            shape_str = f"{shape} [{axis_spec}] [{plane_spec}]"
            k = [shape_str, timing_str, hands]
        elif feat == "joint-specific movements":
            movs = mod["movement details"]["joint specific movement"]
            k = [movs, timing_str, hands]
        elif feat == "handshape change movements":
            k = ["hc", timing_str, hands]
        elif feat == "hand config modules":
            spec = mod["predefined config"]
            k = [spec, timing_str, hands]
        elif feat == "location modules":
            loc = get_loc_str(mod)
            k = [loc, timing_str, hands]
        elif feat == "relation modules":
            mod = assign_assoc_loc_str(sign, mod)
            xs, ys = [], []
           
            for art, spec in mod["X details"].items():
                # "X details": {"H1": {"Whole hand": {"Surface": ["fr"], "Sub-area": []}}}
                xdetails = locn_abbrev(spec)
                if xdetails:
                    art += f" ({xdetails})"
                xs.append(art)
            
            # don't include Y location because this is a problem for minimal pairs
            # if mod["link type"] == "location":
            #     ys = [loc.split(";   ")[0] for loc in mod["linked Y(s)"]]
            # elif mod["link type"] == "body part":
            #     if isinstance(mod["Y details"], str):
            #         print("relation linked body part is not specified", sign["gloss"], sign["corpus source"])
            #     else:
            #         for art, spec in mod["Y details"].items():
            #             ylocs = [y for y in spec if y]
            #             if ylocs:
            #                 art += f"({", ".join(ylocs)})"
            #             ys.append(art)     
            other_info = []
            if mod["has contact"]: 
                other_info.append("contact")
            if mod["dir rel"] not in ["_NA", "_NS"]:
                other_info.append("dir rel")
            if mod["dist rel"] not in ["_NA", "_NS"]:
                other_info.append("dist rel")
            # if not other_info:
            #     print("relation has nothing specified", sign["gloss"], sign["corpus source"])
            other_info = "&".join(other_info)
            k = ["&".join(xs), mod["link type"] if mod["link type"] else "no link", other_info, timing_str]
            # k = [timing_str]

        else:
            print(feat)
        if k:
            k = ";   ".join(k)
            if k in mapping:
                print(f"{feat} duplicate! {k} {s["lemma"]} {s["id"]}")
            mapping[k] = mod 
    return mapping

def map_modules(json_arr):
    for sign in json_arr:

        sign["id"] = int(i)
        for feat in ["perceptual movements", "joint-specific movements", "handshape change movements", "hand config modules", "location modules", "relation modules"]:
            feat_map = map_by(sign, feat)
            sign[feat] = feat_map
            
            
    return json_arr


class Exporter:
    def __init__(self, corpus_source, new_json_path, existing_json_path, export_option, verbose):
        self._corpus_source = corpus_source
        self._new_json_path = new_json_path
        self._existing_json_path = existing_json_path
        self.export_option = export_option
        self.verbose = verbose
        
        self.to_export = [] # signs to append to an existing or blank file
        self.json_arr = [] # pre-existing, loaded from file
        self.inds = {} # maps sign ids to indices 
        self.outfile = None
        self.outfile_option = None # "w" or "a"
        self.newly_added = set()
        self.failed = set()
        
        self.logs = []
        self.set_options()

        
    def set_options(self):
        if self.export_option == "new":
            self.outfile = self._new_json_path
            self.outfile_option = "w"
        elif self.export_option == "append all":
            self.outfile = self._existing_json_path
            self.outfile_option = "a"
        elif self.export_option == "append new":
            self.outfile = self._existing_json_path
            self.json_arr, self.inds = load_jsonl_from_path(self._existing_json_path, verbose=self.verbose)
            self.outfile_option = "a"
        elif self.export_option == "update":
            self.outfile = self._existing_json_path
            self.json_arr, self.inds = load_jsonl_from_path(self._existing_json_path, verbose=self.verbose)
            self.outfile_option = "w"
        else: # update options
            print("option not done yet")
            self.outfile = self._existing_json_path
            self.to_export, self.inds = load_jsonl_from_path(self._existing_json_path, verbose=self.verbose)
            self.outfile_option = "w"


        
    def run(self):
        starttime = datetime.now()
        log_msg(f"Export option: {self.export_option}. Running...", verbose=True)
        corpus_paths = get_corpus_paths(self._corpus_source)
        # new, append all, append new, update, update custom
        if self.export_option in ["new", "append all"]:
            for corpus_path in corpus_paths:
                corpus_obj = load_corpus_binary(corpus_path, as_dict=False, verbose=self.verbose)
                corpus_name = corpus_path.name
                self.to_export.extend(get_corpus_representation(corpus_obj, corpus_name, verbose=self.verbose))
        elif self.export_option == "append new":
            
            for corpus_path in corpus_paths:
                corpus_info = load_corpus_info(corpus_path, verbose=self.verbose)
                # corpus_obj = load_corpus_binary(corpus_path, as_dict=False, verbose=self.verbose)
                corpus_name = corpus_path.name
                skipped_count = 0 
                added_count = 0
                for sign_id in corpus_info:
                    full_id = (*sign_id, corpus_name)
                    if full_id in self.inds:
                        skipped_count += 1
                    elif full_id in self.newly_added:
                        skipped_count += 1
                        msg = f"Warning: corpus source contained a duplicate {full_id}"
                        log_msg(msg, True)
                    else:
                        sign_obj = Sign(serializedsign=corpus_info[sign_id]["serialized sign"])
                        sign_rep = get_sign_representation(sign_obj, corpus_name, verbose=self.verbose)
                        if sign_rep:
                            self.newly_added.add(full_id)
                            self.to_export.append(sign_rep)
                            log_msg(f"   found new sign {full_id}", self.verbose)
                            added_count += 1
                        else:
                            skipped_count += 1
                            self.failed.add(full_id)
                            log_msg(f"   failed to add {full_id} from {corpus_name}. Skipped.", True)
                msg = f"Will append {added_count} from {corpus_name}, skipping {skipped_count}."
                log_msg(msg, self.verbose)
        elif self.export_option == "update":
            for corpus_path in corpus_paths:
                corpus_info = load_corpus_info(corpus_path, verbose=self.verbose)
                # corpus_obj = load_corpus_binary(corpus_path, as_dict=False, verbose=self.verbose)
                corpus_name = corpus_path.name
                skipped_count = 0 
                updated_count = 0
                added_count = 0
                for sign_id in corpus_info:
                    full_id = (*sign_id, corpus_name)
                    if full_id in self.inds: 
                        old_modified_date = self.inds[full_id]["modified"]
                        corpus_modified_date = corpus_info[sign_id]["modified"]
                        
                        if corpus_modified_date - old_modified_date > timedelta(0,1):
                            # we need to replace the outdated sign in self.json_arr
                            json_arr_index = self.inds[full_id]["index"]
                            
                            sign_obj = Sign(serializedsign=corpus_info[sign_id]["serialized sign"])
                            sign_rep = get_sign_representation(sign_obj, corpus_name, verbose=self.verbose)
                            if sign_rep:
                                self.newly_added.add(full_id)
                                self.json_arr[json_arr_index] = sign_rep
                                log_msg(f"   Updated {sign_id}, old modified date {old_modified_date}; new modified date {corpus_modified_date}", self.verbose)
                                updated_count += 1
                            else:
                                skipped_count += 1
                                self.failed.add(full_id)
                                log_msg(f"Failed to update {full_id} from {corpus_name}. Skipped.", self.verbose)

                                                        
                    elif full_id in self.newly_added:
                        skipped_count += 1
                        log_msg(f"Warning: corpus source contained a duplicate {full_id}. Skipped.", self.verbose)
                    else:
                        sign_obj = Sign(serializedsign=corpus_info[sign_id]["serialized sign"])
                        sign_rep = get_sign_representation(sign_obj, corpus_name, verbose=self.verbose)
                        if sign_rep:
                            self.newly_added.add(full_id)
                            self.json_arr.append(sign_rep)
                            log_msg(f"   found new sign {full_id}", self.verbose)
                            added_count += 1
                        else:
                            skipped_count += 1
                            self.failed.add(full_id)
                            log_msg(f"   failed to update {full_id} from {corpus_name}. Skipped.", self.verbose)
                msg = f"Will update {updated_count} signs and add {added_count} signs from {corpus_name}, skipping {skipped_count}."
                log_msg(msg, self.verbose)
                self.to_export = self.json_arr
        else:
            print("not done option", self.export_option)
            # json_arr = load_jsonarr_from_path()   
            # inds = map_to_id(json_arr)
        
        self.to_export = map_modules(self.to_export)
            
        write_jsonl_to_file(self.to_export, self.outfile, self.outfile_option, verbose=self.verbose)
        
        endtime = datetime.now()
        log_msg(f"Done! \nOutput file: {self.outfile}\nLog file: {CONST_OUTPUT_LOG}\nSpent {str(endtime-starttime)}.", verbose=True)
        with open(CONST_OUTPUT_LOG, 'w', encoding='utf-8') as f:
            for msg in logs:
                f.write(msg)
                f.write('\n')
        


if __name__ == '__main__':
    
    exp = Exporter(
        corpus_source=CONST_CORPUS_SOURCE,
        new_json_path=CONST_NEW_JSONL_PATH,
        existing_json_path=CONST_EXISTING_JSONL_PATH,
        export_option=CONST_EXPORT_OPTION,
        verbose=False
    )
    
    
    exp.run()


    

    
# parser=argparse.ArgumentParser()
# parser.add_argument("command", choices=['export', 'update', 'run'])
# parser.add_argument("--infiles", "-i", action='extend', nargs='+', help='One or multiple .slpaa corpora')
# parser.add_argument("--outfile", "-o", help='JSON file to create or update')
# args=parser.parse_args()



# if args.command == 'run':
#     jsonarr = []
#     outfile = args.outfile if args.outfile else 'output.json'
#     try:
#         with open(outfile, 'r') as f:
#             jsonarr = json.load(f)
#     except:
#         print(f"couldn't open {args.outfile}")
            
            
#     update_specific_module(ModuleTypes.LOCATION, jsonarr)
            
#     with open(outfile, 'w') as f:
#         json.dump(jsonarr, f)

# else:
#     jsonarr = []
#     outfile = args.outfile if args.outfile else 'output.json'

            
#     for f in args.infiles:
#         corpus = load_corpus_binary(f)
#         corpus_name = Path(f).name
#         if args.command == 'export':
#             signlist = get_corpus_representation(corpus, corpus_name)
            
#             jsonarr.extend(signlist)
#         else:
#             print('not done')
            
#     with open(outfile, 'w') as f:
#         json.dump(jsonarr, f)