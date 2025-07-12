import streamlit as st
from src.answer_generator import AnswerGenerator
from src.logger import log_mismatch_case

generator = AnswerGenerator()

st.set_page_config(page_title="AI First-Aid Assistant 💊", layout="wide")
st.title("🩺 AI-Powered First-Aid Assistant")

if "verified_condition" not in st.session_state:
    st.session_state.verified_condition = ""
if "triage_needs_check" not in st.session_state:
    st.session_state.triage_needs_check = False

# Input box
user_query = st.text_area("Describe your symptoms", height=100)

if st.button("Get First-Aid Advice"):
    with st.spinner("Analyzing..."):
        answer, condition, ranked = generator.generate_answer(user_query)

    # Display output immediately
    st.session_state.answer = answer
    st.session_state.condition = condition
    st.session_state.ranked = ranked
    st.session_state.triage_needs_check = True  # Trigger triage next run

# Display result if available
if "answer" in st.session_state:
    st.markdown(f"### 🧠 Likely Condition: `{st.session_state.condition}`")
    st.markdown("### 💡 First-Aid Advice:")
    st.markdown(st.session_state.answer)

    with st.expander("📚 Evidence Used"):
        for item in st.session_state.ranked:
            st.markdown(f"- {item['citation_label']} **{item['source'].capitalize()}**: {item['text']}")

    with st.expander("🔗 Sources"):
        for item in st.session_state.ranked:
            if item["source"] == "web" and "url" in item:
                st.markdown(f"{item['citation_label']} → [View Source]({item['url']})")

    # Run Gemini triage verification AFTER output shown
    if st.session_state.triage_needs_check:
        with st.spinner("Running triage verification..."):
            verified = generator.traig.gemini_fallback(user_query).strip()
            st.session_state.verified_condition = verified
            st.session_state.triage_needs_check = False

            if verified.lower() != st.session_state.condition.lower():
                log_mismatch_case(
                    query=user_query,
                    original_condition=st.session_state.condition,
                    verified_condition=verified,
                    answer=st.session_state.answer,
                    evidence_list=st.session_state.ranked
                )
                st.info("🔍 Gemini flagged a triage mismatch — it has been logged for review.")

    if st.button("Report error"):
        log_mismatch_case(
            query=user_query,
            original_condition=st.session_state.condition,
            verified_condition=st.session_state.verified_condition,
            answer=st.session_state.answer,
            evidence_list=st.session_state.ranked
        )
        st.info("Error flagged and saved.")

    st.markdown("⚠️ This information is for educational purposes only and is not a substitute for professional medical advice.")
