import spacy

nlp = spacy.load("en_core_web_sm")

text = """
I have a project that includes making a social media campaign for
all platforms. The product is perfume, age ranges from 17-30 and it's
an elite brand. They want to sell it to the Middle East audience.
"""

doc = nlp(text)

extract_requirements = {
    "product": None,
    "age_range": None,
    "market": None,
    "brand_positioning": None,
    "campaign_type": None,
    "platforms": None
}


# 1. PRODUCT
for token in doc:
    if token.text.lower() == "product":

        for child in token.head.children:
            if child.pos_ == "NOUN" and child.text.lower() != "product":
                extract_requirements["product"] = child.text


# 2. AGE RANGE
for token in doc:
    if token.text.lower() == "age":

        for child in token.head.children:
            if child.text.lower() == "from":

                numbers = []

                for number in child.children:
                    if number.pos_ == "NUM":
                        numbers.append(number.text)

                        for next_number in number.children:
                            if next_number.pos_ == "NUM":
                                numbers.append(next_number.text)

                if numbers:
                    extract_requirements["age_range"] = "-".join(numbers)


# 3. MARKET
for token in doc:
    if token.text.lower() == "sell":

        for child in token.children:
            if child.text.lower() == "to":

                for word in child.children:
                    if word.text.lower() == "audience":

                        market_words = []

                        for market in word.children:
                            if market.pos_ == "PROPN":
                                market_words.append(market.text)

                                for subword in market.children:
                                    if subword.pos_ == "PROPN":
                                        market_words.append(subword.text)

                        extract_requirements["market"] = " ".join(reversed(market_words))


# 4. BRAND POSITIONING
for token in doc:
    if token.text.lower() == "brand":

        for child in token.children:
            if child.dep_ == "amod":
                extract_requirements["brand_positioning"] = child.text


# 5. CAMPAIGN TYPE
for token in doc:
    if token.text.lower() == "campaign":

        words = []

        for child in token.children:
            words.append(child.text)

        words.append(token.text)

        extract_requirements["campaign_type"] = " ".join(words)


# 6. PLATFORMS
for token in doc:
    if token.text.lower() == "platforms":

        words = []

        for child in token.children:
            if child.dep_ == "det":
                words.append(child.text)

        words.append(token.text)

        extract_requirements["platforms"] = " ".join(words)


print(extract_requirements)

