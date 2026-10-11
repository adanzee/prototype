def generate_recommendation(requirements, relevant_knowledge):

    recommendation = {
        "product": requirements["product"],
        "target_age": requirements["age_range"],
        "market": requirements["market"],
        "brand_positioning": requirements["brand_positioning"],
        "campaign_type": requirements["campaign_type"],
        "platforms": requirements["platforms"],
        "design_direction": [],
        "knowledge_used": []
    }

    for entry in relevant_knowledge:

        recommendation["knowledge_used"].append({
            "title": entry["title"],
            "source": entry["source"],
            "content": entry["content"]
        })

    # Basic prototype rules
    if requirements["brand_positioning"].lower() in ["elite", "luxury", "premium"]:
        recommendation["design_direction"].append(
            "Use a premium and sophisticated visual style."
        )

    if requirements["product"].lower() == "perfume":
        recommendation["design_direction"].append(
            "Use imagery and composition that communicate fragrance, elegance and exclusivity."
        )

    if requirements["market"].lower() == "middle east":
        recommendation["design_direction"].append(
            "Consider Middle Eastern cultural context and visual preferences."
        )

    recommendation["design_direction"].append(
        "Keep the design suitable for social media platforms."
    )

    return recommendation