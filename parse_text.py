import re

with open('dictionary_text_extraction.txt', encoding='utf-8') as f:
    text = f.read()

#there's a lot of random newline characters we need to get rid of, as well as commas which mess up csv files
unwanted_chars = '\n,:'
translation_table = str.maketrans('', '', unwanted_chars)
pos_tags = ['n.', 'v.', 'adj.', 'adv.', 'pron.', 'onj.']

#identify the beginning of each definition by looking for a lower-case word followed by a colon
#this pattern returns spans of text between matches
pattern = r'([a-z]+):\s*([\s\S]*?)(?=[a-z]+:|$)'
matches = re.findall(pattern, text, flags=re.DOTALL)

output_dictionary = dict()
for match in matches:
    gloss = match[0].strip().replace(',','').translate(translation_table).upper()
    description = match[1]
    description = description.replace('THE CANADIAN DICTIONARY OF ASL', '') #this seems to be a footer?
    #the next regex tries to find instances of the word "SIGN:" which should be followed by descriptions
    #each match includes the span of text between the matches
    #pattern_sign = r'SIGN\d*(.*?)\s*:([\s\S]*?)(?=[a-z]+:|$)'
    #sign_matches = re.findall(pattern_sign, description, flags=re.DOTALL)

    sign_matches = [d.strip(u'0x0c') for d in description.lower().split('sign')]
    sign_matches = [m.strip(';').strip() for m in sign_matches]
    if not sign_matches:
        continue
    sign_matches = [m for m in sign_matches if not any(tag in m for tag in pos_tags)]
    sign_matches = [m for m in sign_matches if not any(m.startswith(x) for x in ['-', '—'])]
    sign_matches = [m for m in sign_matches if len(m.split(' '))>10]
    descriptions = [m.translate(translation_table) for m in sign_matches]

    for i,d in enumerate(descriptions):
        if d.startswith('¹'):
            descriptions[i] = d[2:]
    if len(descriptions) == 1:
        output_dictionary[gloss] = descriptions[0]
    elif len(descriptions) > 1:
        for i, d in enumerate(descriptions):
            v_gloss = f'{gloss} (v.{i+1})'
            output_dictionary[v_gloss] = d


with open('gloss_to_description.csv', encoding='utf-8', mode='w') as f:
    for key,value in output_dictionary.items():
        print('\t'.join([key,value]), file=f)