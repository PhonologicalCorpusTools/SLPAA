import json
from string import ascii_uppercase

def handshape_only(data):
    transcriptions = dict()
    for blob in data['signs']:
        gloss = blob['signlevel']['gloss'][0].replace(',','')
        transcription = list()
        try:
            for number in blob['cfg module numbers']:
                for field in blob['cfg modules'][number]['_handconfiguration']:
                    for slot in field['slots']:
                        try:
                            transcription.append(slot['symbol'])
                        except KeyError: #no symbol entered by annotator?
                            transcription.append('-')
        except KeyError:#no cfg module number
            pass
        transcriptions[gloss] = ''.join(transcription)

    return transcriptions

def full_parse(data):
    new_json = {}

    for blob in data['signs']:
        print(blob['signlevel']['gloss'])
        # new_json['type'] = {}
        # new_json['type']['_specslist'] = blob['type']['_specslist']
        new_blob = {}

        gloss = blob['signlevel']['gloss'][0].split('(')[0].lower().strip()

        #new_blob['gloss'] = blob['signlevel']['gloss']

        if 'mov module numbers' in blob:
            new_blob['mov modules'] = {}
            for index,id in enumerate(blob['mov module numbers']):
                letter_id = ascii_uppercase[index]
                new_blob['mov modules'][letter_id] = {}
                new_blob['mov modules'][letter_id]['movementtree'] = {}
                new_blob['mov modules'][letter_id]['movementtree']['checkstates'] = blob['mov modules'][id]['movementtree']['checkstates']
        if 'cfg module numbers' in blob:
            new_blob['cfg module numbers'] = {}
            for index,id in enumerate(blob['cfg module numbers']):
                letter_id = ascii_uppercase[index]
                new_blob['cfg module numbers'][letter_id] = {}
                new_blob['cfg module numbers'][letter_id]['_handconfiguration'] = blob['cfg modules'][id]['_handconfiguration']

        if 'loc module numbers' in blob:
            new_blob['loc module numbers'] = {}
            for index,id in enumerate(blob['loc module numbers']):
                letter_id = ascii_uppercase[index]
                new_blob['loc module numbers'][letter_id] = {}
                new_blob['loc module numbers'][letter_id]['locationtree'] = blob['loc modules'][id]['locationtree']

        new_json[gloss] = new_blob

    with open('features_for_t5.json', encoding='utf-8', mode='w') as f:
        json.dump(new_json, f)

def predefined_shapes():
    with open('predefined_shapes.csv', encoding='utf-8') as f:
        header = f.readline()
        lines = [line.strip() for line in f]
    shapes = dict()
    for line in lines:
        name, transcription = line.split(',', maxsplit=1)
        transcription = ''.join(transcription.split(','))
        shapes[transcription] = name
    return shapes

def get_slpa_transcriptions():
    with open('minimal.json') as f:
        data = json.load(f)
    hs = handshape_only(data)
    with open('gloss_to_transcription.csv', mode='w', encoding='utf-8') as f:
        for gloss, transcription in hs.items():
            f.write('\t'.join([gloss, transcription]))
            f.write('\n')

    shapes = predefined_shapes()
    unrecognized = list()
    with open('gloss_to_handshape.csv', mode='w', encoding='utf-8') as f:
        for gloss,transcription in hs.items():
            try:
                shape = shapes[transcription]
                f.write(','.join([gloss, shape]))
                f.write('\n')
                #print(f'Matched {transcription}')
            except KeyError:
                unrecognized.append(','.join([gloss, transcription]))
                #print(f'No match for {transcription}')

    with open('unrecognized_shape.csv', mode='a', encoding='utf-8') as f2:
        f2.write('\n'.join(unrecognized))
        # print(f"Couldn't match the transcription for {gloss} {transcription} to any pre-defined handshape")

if __name__ == '__main__':
    get_slpa_transcriptions()