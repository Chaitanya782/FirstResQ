import os
import google.generativeai as genai

from src.Aggregator import DataAggregator
from src.triage_module import traiger
import json

class AnswerGenerator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.traig=traiger()
        self.aggregator=DataAggregator()

    def build_citation_section(self, evidence_list):
        lines = []
        for e in evidence_list:
            label = e.get("citation_label")
            text = e["text"]
            if e["source"] == "web" and "url" in e:
                lines.append(f"{label} Web: {e['url']}")
            else:
                lines.append(f"{label} Local: {text}")
        return "\n".join(lines)

    def generate_answer(self, query):
        condition=self.traig.classify_symptom(query)
        evidence_list=self.aggregator.merge_data(query, condition)
        formatted_list = "\n".join(
            f'{e["citation_label"]} {e["source"].capitalize()}: "{e["text"]}"'
            for e in evidence_list
        )

        prompt = f"""
        You are a compassionate and knowledgeable medical first-aid assistant.

        Your role is to analyze the patient’s symptom description, identify the most likely medical condition, and provide **clear, grouped, evidence-based first-aid steps**.

        You must **only use the provided evidence** to generate the response. Do not invent symptoms, make assumptions, or introduce treatments not directly supported by the citations.

        ---

        🩺 Patient Symptom Description:
        {query}

        ---

        🩺 Most Likely Condition:
        {condition}

        ---

        📚 Supporting Medical Evidence:
        {formatted_list}  # Use [1], [2], etc., for evidence references

        ---

        📝 Response Instructions:
        - Begin with 1–2 plain-language sentences explaining the likely condition and its seriousness.
        - Then provide 3–5 first-aid steps, **grouped logically** (e.g., 🚨 Emergency Action, 💧 Hydration, 💊 Monitoring, etc.)
        - Ensure each step is supported by the evidence using citation labels like [1], [2].
        - Avoid repeating the same message (e.g., don’t say “seek help” in multiple places).
        - **If the query includes "unconscious", "bleeding", or "seizure"**, start the response with this exact line:
          **"🚨 Please call emergency services immediately."**
        - Mention only medications or treatments found in the evidence.
        - Use a calm, warm, and instructive tone—like a nurse gently guiding someone in distress.
        - Keep the total word count under 250.
        - End with this exact disclaimer:

        ⚠ This information is for educational purposes only and is not a substitute for professional medical advice.
        """

        response=self.model.generate_content(prompt)

        final_output = response.text.strip() + "\n\n📚 Sources:\n" + self.build_citation_section(evidence_list)

        # print(final_output)
        return response.text, condition, evidence_list

if __name__ == "__main__":
    ans=AnswerGenerator()
    ans.generate_answer("After working in the sun all day I’ve barely urinated and my creatinine just rose 0.4 mg/dL—could this be acute kidney injury and what should I do?")
