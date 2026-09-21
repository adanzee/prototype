import spacy

# Load a standard English pipeline
nlp = spacy.load("en_core_web_sm")

# 1. Get a simple list of component names
print("Component names:", nlp.pipe_names)
# Output: ['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer', 'ner']

# 2. Get a detailed list of (name, component) tuples
print("Detailed pipeline:", nlp.pipeline)
print("visual cmd")
nlp.analyze_pipes(pretty=True)