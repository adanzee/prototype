knowledge = [
    {
        "id": 1,
        "source_type": "research",
        "title": "Example Research",
        "topic": "visual attention",
        "market": "general",
        "product": "general",
        "content": "Research finding goes here.",
        "source": "Paper or article name"
    }
    ,
        {
        "id": 2,
        "source_type": "research",
        "title": "Another Research",
        "topic": "luxury branding",
        "market": "general",
        "product": "perfume",
        "content": "Another research finding goes here.",
        "source": "Another paper"
    },

    {
    "id": 3,
    "source_type": "campaign",
    "title": "Example Perfume Campaign",
    "topic": "luxury perfume",
    "market": "Middle East",
    "product": "perfume",
    "content": "Luxury perfume campaign targeting young adults through social media.",
    "source": "Example Campaign"
    }
]

def retrieve_knowledge(requirements):
    relevant_knowledge = []

    for entry in knowledge:
        product_match = (
            entry["product"].lower() == requirements["product"].lower()
            or entry["product"].lower() == "general"
        )

        market_match = (
            entry["market"].lower() == requirements["market"].lower()
            or entry["market"].lower() == "general"
        )

        if product_match and market_match:
            relevant_knowledge.append(entry)

    return relevant_knowledge

print(knowledge)