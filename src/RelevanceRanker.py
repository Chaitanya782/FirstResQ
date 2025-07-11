import re

TRUSTED_DOMAINS = ["mayoclinic.org", "nhsinform.scot", "redcross.org", "clevelandclinic.org", "cdc.gov"]
UNTRUSTED_DOMAINS = ["quora.com", "reddit.com", "wikihow.com"]


class RelevanceRanker():
    def __init__(self):
        pass

    def _keyword_score(self, query, text):
        query_keywords = re.findall(r'\w+', query.lower())
        text_lower = text.lower()
        return sum(1 for word in query_keywords if word in text_lower)

    def _source_score(self, source):
        return 2 if source == "local" else 0.5

    def _domain_score(self, url, keyword_score):
        if not url:
            return 0
        if any(trusted in url for trusted in TRUSTED_DOMAINS) and keyword_score >= 2:
            return 1
        if any(untrusted in url for untrusted in UNTRUSTED_DOMAINS):
            return -2
        return 0

    def rank(self, query, combined_list, top_k=5):
        scored=[]
        for i, item in enumerate(combined_list):
            item["citation_label"] = f"[{i + 1}]"

        for item in combined_list:
            base_score=0
            base_score += self._keyword_score(query, item["text"])
            base_score += self._domain_score(item.get("url", ""), base_score)
            base_score += self._source_score(item.get("source", ""))
            item["score"] = base_score
            scored.append(item)
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]