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

        Use only the evidence provided to generate your response. Do not add new information, make assumptions, or hallucinate facts. Your goal is to clearly explain the likely condition and recommend helpful first-aid steps based on the patient’s description and the supporting evidence.

        ---

        🩺 Patient Symptom Description:
        {query}

        ---

        🩺 Most Likely Condition:
        {condition}

        ---

        📚 Supporting Medical Evidence:
        {formatted_list}  # Use [1], [2], etc. with evidence sentences

        ---

        📝 Response Instructions:
        - Begin with 1–2 sentences that gently explain the likely condition in plain language.
        - Provide 3–5 clearly formatted first-aid steps or actions the user should consider and keep gruped dsteps together.
        - Mention key medicines or treatment options, only if found in the evidence.
        - Use citation labels like [1], [2], etc., to support your recommendations.
        - Write in a warm, calm tone — as if you are a nurse or first-aid expert speaking directly to the person.
        - If query includes "unconscious", "bleeding", "seizure", show:
            "Please call emergency services immediately."
        - Keep the response under 250 words.
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
