from design_analysis import analyze_design
from recommendation import generate_recommendation
from knowledge import retrieve_knowledge

requirements = {
    "product": "perfume",
    "age_range": "17-30",
    "market": "Middle East",
    "brand_positioning": "elite",
    "campaign_type": "a social media campaign",
    "platforms": "all platforms"
}

relevant_knowledge = retrieve_knowledge(requirements)

recommendation = generate_recommendation(
    requirements,
    relevant_knowledge
)

result = analyze_design(
    "windows_screen.png",
    requirements,
    recommendation
)

print(result)