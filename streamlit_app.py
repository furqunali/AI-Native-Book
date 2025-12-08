import streamlit as st
import random

st.title("Future AI Scenario Generator (Simulated)")

st.write("Enter a concept and imagine how AI might transform it in the future.")
st.write("e.g., Personalized healthcare, Autonomous driving, Creative arts...")

# Input from the user
concept = st.text_input("Enter your concept:")

# Button to generate scenario
if st.button("Generate Scenario"):
    if concept.strip() == "":
        st.warning("Please enter a concept to generate a scenario.")
    else:
        # Simulated AI scenarios (you can expand these)
        scenarios = [
            f"In the future, AI will revolutionize {concept} by making it fully autonomous and personalized.",
            f"{concept} will be enhanced by AI, leading to previously impossible innovations and efficiencies.",
            f"With AI, {concept} will become smarter, faster, and accessible to everyone globally.",
            f"AI will transform {concept}, blending human creativity and machine intelligence seamlessly."
        ]
        scenario = random.choice(scenarios)
        st.success("Generated Future Scenario:")
        st.info(scenario)

st.write("Enter a concept and click 'Generate Scenario' to see a speculative AI future.")


