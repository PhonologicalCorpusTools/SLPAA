import argparse, json
from pathlib import Path
from lexicon.lexicon_classes import Sign, Corpus, unserializelocationmodules, unserializemovementmodules, unserializerelationmodules 
from serialization_classes import renamed_load
# from fbs_runtime.application_context.PyQt5 import ApplicationContext
# from PyQt5.QtWidgets import (
#     QFileDialog
# )

parser=argparse.ArgumentParser()
parser.add_argument("command", choices=['export', 'update'])
parser.add_argument("--infiles", "-i", action='extend', nargs='+', help='One or multiple .slpaa corpora')
parser.add_argument("--outfile", "-o", help='JSON file to create or update')
args=parser.parse_args()



def load_corpus_binary(path):
    with open(path, 'rb') as f:
        corpus = Corpus(serializedcorpus=renamed_load(f))
        # in case we're loading a corpus that was originally created on a different machine / in a different folder
        corpus.path = path
        return corpus

def get_corpus_representation(corpus: Corpus, name):
    signlist = []
    for sign in corpus.signs:
        sign_rep = sign.full_info()
        sign_rep["corpus source"] = name
        signlist.append(sign_rep)
    return signlist
    

jsonarr = []
outfile = args.outfile if args.outfile else 'output.json'
if args.outfile:
    try:
        with open(outfile, 'r') as f:
            jsonarr = json.loads(f)
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