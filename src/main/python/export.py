import argparse, json, traceback
from pathlib import Path
from datetime import datetime
from lexicon.lexicon_classes import Sign, Corpus, unserializelocationmodules, unserializemovementmodules, unserializerelationmodules 
from serialization_classes import renamed_load
from constant import ModuleTypes
import logging
logging.disable(logging.WARNING)

""" Specify the source of .slpaa files. 
Options are: 
- a list of paths
- a single path
- a single directory
"""
CONST_CORPUS_SOURCE = "/home/grace/Projects/SLPAA/to_export/all"

""" Specify output path or None. If the file doesn't exist, it will be created. Can be the same as CONST_EXISTING_JSONL_PATH. """
CONST_NEW_JSONL_PATH = "/home/grace/Projects/SLPAA/SLPAA/src/main/python/export/allsigns.jsonl"

""" Specify existing JSONL filepath, or None. """
CONST_EXISTING_JSONL_PATH = "/home/grace/Projects/SLPAA/SLPAA/src/main/python/export/exported.jsonl"

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
CONST_EXPORT_OPTION = "new"

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
    if verbose:
        print(f"Successfully {"wrote" if option == 'w' else "appended" if option == 'a' else ""} {counter} signs to {outfile}")
        
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
    # also returns a map
    mapping = {}
    jsonarr = []
    counter = 0
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                sign_dict = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON on line: {line.strip()[0:30]}.... Error: {e}")
            else:
                id = (sign_dict["entryid"], sign_dict["lemma"], sign_dict["corpus source"])
                jsonarr.append(sign_dict)
                if id in mapping:
                    print(f"warning: skipped duplicate {id} in {path}")
                else:
                    mapping[id] = counter
            counter += 1
    if verbose:
        print(f"Loaded {len(mapping)} out of {counter} signs from {path}.")
    return jsonarr, mapping


def load_corpus_binary(path, corpus_dir = None, as_dict = False, verbose=False):
    # as_dict = True: loads as a dict with (lemma, entryid) as keys and sign objects as values, for quick lookup
    if corpus_dir:
        path = Path(corpus_dir) / path
    
    
    with open(path, 'rb') as f:
        corpus = Corpus(serializedcorpus=renamed_load(f))
        # in case we're loading a corpus that was originally created on a different machine / in a different folder
        corpus.path = path
        if verbose: print(f"Loaded corpus binary {path} containing {len(corpus.signs)} signs.")
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
            "datetime": datetime.fromtimestamp(slinfo['date last modified']) 
        }
        # sli["date last modified"] = self._signlevel_information.datelastmodified.strftime('%Y-%m-%d %I:%M:%S%p')
        
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
        print(traceback.format_exc())
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
            print(f"Couldn't add {sign_id} from {corpus_name}. Skipped.")
    return signlist

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
        else: # update options
            print("option not done yet")
            self.outfile = self._existing_json_path
            self.to_export, self.inds = load_jsonl_from_path(self._existing_json_path, verbose=self.verbose)
            self.outfile_option = "w"

        
    def run(self):
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
                        print(f"Warning: corpus source contained a duplicate {full_id}")
                    else:
                        sign_obj = Sign(serializedsign=corpus_info[sign_id]["serialized sign"])
                        sign_rep = get_sign_representation(sign_obj, corpus_name, verbose=self.verbose)
                        if sign_rep:
                            self.newly_added.add(full_id)
                            self.to_export.append(sign_rep)
                            if self.verbose: print(f"   found new sign {full_id}")
                            added_count += 1
                        else:
                            skipped_count += 1
                            self.failed.add(full_id)
                            print(f"Failed to add {full_id} from {corpus_name}. Skipped.")
                if self.verbose: print(f"Will append {added_count} from {corpus_name}, skipping {skipped_count}.")
        else:
            print("not done option", self.export_option)
            # json_arr = load_jsonarr_from_path()   
            # inds = map_to_id(json_arr)
            
        write_jsonl_to_file(self.to_export, self.outfile, self.outfile_option, verbose=self.verbose)
        
            
            

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