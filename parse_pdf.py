import pymupdf

doc = pymupdf.open("docs/dictionary.pdf") # open a document
out = open("dictionary_text_extraction.txt", "wb") # create a text output

for page in doc: # iterate the document pages
    text = page.get_text().encode("utf8") # get plain text (is in UTF-8)
    out.write(text) # write text of page
    out.write(bytes((12,))) # write page delimiter (form feed 0x0C)
out.close()