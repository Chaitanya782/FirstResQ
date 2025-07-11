import os
import google.generativeai as genai
import json
import requests
from src.triage_module import traiger


class web_player():
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.serper_key=os.getenv("SERPER_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
        self.traig=traiger()

    def gemini_querifier(self, query):
        prompt=f"""
        Given the following patient query:
         {query}
        create a single concise, search-optimized query to find relevant first aid advice.
        Just give the seach query, nothing else.
        """
        query = self.model.generate_content(prompt)
        # print(query.text.strip())
        return query.text.strip()

    def gemini_fallback(self, query, condition):

        return f"first aid for {query} {condition}".strip()

    def _get_query(self, query, condition):
        try:
            # print("*")
            search_query=self.gemini_querifier(query)
            # print("**")
        except Exception as e:
            print("Gemini error : ",e)
            search_query=self.gemini_fallback(query, condition)
        return search_query

    def web_crawler(self, query, condition):
        search_query = self._get_query(query, condition)

        url = "https://google.serper.dev/search"

        payload = json.dumps({
            "q": search_query
        })
        headers = {
            'X-API-KEY': self.serper_key,
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        data = response.json()
        # if "organic" in data:
        #     for result in data["organic"][:3]:
        #         print("🔹 Title:", result["title"])
        #         print("📄 Snippet:", result["snippet"])
        #         print("🔗 URL:", result["link"])
        #         print("-----")
        # else:
        #     print("⚠️ No search results found.")

        results = [
            {
                "text": r["snippet"],
                "source": "web",
                "url": r["link"]
            }
            for r in data["organic"]
        ]

        return results

if __name__ == "__main__":
    web = web_player()
    web.web_crawler("I'm sweating, glucose 55, feel dizzy")
