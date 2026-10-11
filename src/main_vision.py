from document_parser import process_text
from pos_context import extract_requirements

from knowledge import retrieve_knowledge

from recommendation import generate_recommendation

from screen_capture import capture_screen

from design_analysis import analyze_design


def main():

    text = """
    I have a project that includes making a social media campaign
    for all platforms. The product is perfume, age ranges from 17-30
    and it's an elite brand. They want to sell it to the Middle East audience.
    """

    # -------------------------
    # 1. Process input
    # -------------------------

    processed_text = process_text(text)

    print("\nProcessed input:")
    print(processed_text)


    # -------------------------
    # 2. Extract requirements
    # -------------------------

    requirements = extract_requirements(processed_text)

    print("\nRequirements:")
    print(requirements)


    # -------------------------
    # 3. Retrieve knowledge
    # -------------------------

    relevant_knowledge = retrieve_knowledge(requirements)

    print("\nRelevant knowledge:")

    for entry in relevant_knowledge:
        print(
            entry["title"],
            "->",
            entry["source"]
        )


    # -------------------------
    # 4. Generate recommendation
    # -------------------------

    recommendation = generate_recommendation(
        requirements,
        relevant_knowledge
    )

    print("\nInitial recommendation:")

    for direction in recommendation["design_direction"]:
        print("-", direction)


    # -------------------------
    # 5. Capture screen
    # -------------------------

    print("\nCapturing screen...")

    screenshot_path = capture_screen()

    print("Screenshot:", screenshot_path)


    # -------------------------
    # 6. Analyze design
    # -------------------------

    print("\nAnalyzing design...")

    design_analysis = analyze_design(
        screenshot_path,
        requirements,
        recommendation
    )

    print("\nDesign analysis:")
    print(design_analysis)


    # -------------------------
    # 7. Final output
    # -------------------------

    print("\n==============================")
    print("FINAL DESIGN RECOMMENDATION")
    print("==============================")

    print("\nRequirements:")
    for key, value in requirements.items():
        print(f"{key}: {value}")

    print("\nDesign direction:")

    for direction in recommendation["design_direction"]:
        print("-", direction)

    print("\nExisting design analysis:")
    print(design_analysis)


if __name__ == "__main__":
    main()