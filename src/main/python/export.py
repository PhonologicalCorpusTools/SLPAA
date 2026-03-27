import argparse, json
from pathlib import Path
from lexicon.lexicon_classes import Sign, Corpus, unserializelocationmodules, unserializemovementmodules, unserializerelationmodules 
from serialization_classes import renamed_load
from constant import ModuleTypes
# from fbs_runtime.application_context.PyQt5 import ApplicationContext
# from PyQt5.QtWidgets import (
#     QFileDialog
# )

parser=argparse.ArgumentParser()
parser.add_argument("command", choices=['export', 'update', 'run'])
parser.add_argument("--infiles", "-i", action='extend', nargs='+', help='One or multiple .slpaa corpora')
parser.add_argument("--outfile", "-o", help='JSON file to create or update')
args=parser.parse_args()



def load_corpus_binary(path, corpus_dir = None, as_dict = False):
    # as_dict = True: loads as a dict with (lemma, entryid) as keys and sign objects as values, for quick lookup
    if corpus_dir:
        path = Path(corpus_dir) / path
    
    try:
        with open(path, 'rb') as f:
            corpus = Corpus(serializedcorpus=renamed_load(f))
            # in case we're loading a corpus that was originally created on a different machine / in a different folder
            corpus.path = path
    except:
        print('failed to open', path)
    
    if as_dict:
        corpus_dict = {}
        for sign in corpus:
            id = (sign._signlevel_information._entryid.counter, sign._signlevel_information.lemma)
            corpus_dict[id] = sign
        return corpus_dict
    else:
        return corpus

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

def get_corpus_representation(corpus: Corpus, name):
    signlist = []
    for sign in corpus.signs:
        sign_rep = sign.full_info()
        sign_rep["corpus source"] = name
        signlist.append(sign_rep)
    return signlist

if args.command == 'run':
    jsonarr = []
    outfile = args.outfile if args.outfile else 'output.json'
    try:
        with open(outfile, 'r') as f:
            jsonarr = json.load(f)
    except:
        print(f"couldn't open {args.outfile}")
            
            
    update_specific_module(ModuleTypes.LOCATION, jsonarr)
            
    with open(outfile, 'w') as f:
        json.dump(jsonarr, f)

else:
    jsonarr = []
    outfile = args.outfile if args.outfile else 'output.json'
    if args.outfile:
        try:
            with open(outfile, 'r') as f:
                jsonarr = json.load(f)
        except:
            print(f"couldn't open {args.outfile}")
            
            
    for f in args.infiles:
        corpus = load_corpus_binary(f)
        corpus_name = Path(f).name
        if args.command == 'export':
            signlist = get_corpus_representation(corpus, corpus_name)
            
            jsonarr.extend(signlist)
        else:
            print('not done')
            
    with open(outfile, 'w') as f:
        json.dump(jsonarr, f)