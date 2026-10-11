import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("Aurelia is launching a floral perfume in the UAE.")

for ent in doc.ents:
    print(ent.text, ent.label_)