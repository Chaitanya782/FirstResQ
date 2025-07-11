import streamlit as st
from src.answer_generator import AnswerGenerator



generator = AnswerGenerator()

st.set_page_config(page_title="AI First-Aid Assistant 💊", layout="wide")
st.title("🩺 AI-Powered First-Aid Assistant")

# Input box
user_query = st.text_area("Describe your symptoms", height=100)

if st.button("Get First-Aid Advice"):
    with st.spinner("Analyzing..."):
        answer, condition, ranked = generator.generate_answer(user_query)

    # Output
    st.markdown(f"### 🧠 Likely Condition: `{condition}`")
    st.markdown("### 💡 First-Aid Advice:")
    st.markdown(answer)

    with st.expander("📚 Evidence Used"):
        for item in ranked:
            st.markdown(f"- {item['citation_label']} **{item['source'].capitalize()}**: {item['text']}")

    with st.expander("🔗 Sources"):
        for item in ranked:
            if item["source"] == "web" and "url" in item:
                st.markdown(f"{item['citation_label']} → [View Source]({item['url']})")

    st.markdown("⚠️ This information is for educational purposes only and is not a substitute for professional medical advice.")
