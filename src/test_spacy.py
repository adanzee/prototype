import spacy 
from spacy import displacy
nlp = spacy.load("en_core_web_sm")
text = """
I have a project that includes making a social media campaign for all platforms. The product is perfume, age ranges from 17-30 and it's an elite brand. They want to sell it to the Middle East audience.
"""

doc = nlp(text)
# (_) underscore after any nlp to return the human readable string  
#human readable with POS
for token in doc:
    print(f"\033[33m{token.text} -> {token.pos_}\033[0m")

print("="*10)
#numerical format
for token in doc:
    print(f"\033[31m{token.text}, ->, {token.pos}\033[0m")
# simple text
for token in doc:
    print(f"\033[32m{repr(token.text)}\033[0m")
#check dependecy parsing 
for token in doc:
    print(token.text, "->", token.dep_, "->", token.head.text)
#relationship
print('relationship')
for token in doc:
    print(token.text, "->", token.dep_, "->", token.head.text)

#NER
for entity in doc.ents:
    print(entity.text, "->", entity.label_)
    if entity.label_ == "LOC":
        market = entity.text
        print(market)
    elif entity.label_ == "CARDINAL":
        age_range = entity.text
        print(age_range)
#dependecy parsing test 

displacy.render(doc, style="dep")
    
