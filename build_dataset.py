import json

with open('gloss_to_handshape.csv') as f:
    gloss_to_handshape = dict()
    for line in f:
        line = line.strip()
        if line:
            gloss, shape = line.split(',')
            gloss_to_handshape[gloss] = shape

with open('gloss_to_description.csv', encoding='utf-8') as f:
    gloss_to_description = dict()
    header = f.readline()
    for line in f:
        line = line.strip()
        if line:
            gloss, description = line.split('\t')
            gloss_to_description[gloss.lower()] = description

in_out = list()
for gloss,shape in gloss_to_handshape.items():
    try:
        description = gloss_to_description[gloss.lower()]
        prompt = 'Summarize: '+ description
        prediction = shape + ' </s>' #EOS token for T5
        in_out.append('\t'.join([prompt, shape]))
    except KeyError:
        print(f'{gloss} has a predefined handshape in SLPA but cannot be found in the dictionary')


with open('input_output.csv', encoding='utf-8', mode='w') as f:
    f.write('input_text\ttarget_text')
    f.write('\n')
    f.write('\n'.join(in_out))