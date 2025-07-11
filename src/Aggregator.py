from src.RelevanceRanker import RelevanceRanker
from src.local_retriever import retrieve_local_relevant_sentences
from src.web_retriever import web_player
from concurrent.futures import ThreadPoolExecutor

class DataAggregator():
    def __init__(self):
        self.web_retriever=web_player()
        self.ranker=RelevanceRanker()

    def _local_data(self, query):
        return retrieve_local_relevant_sentences(query)

    def _web_data(self, query, condition):
        return self.web_retriever.web_crawler(query, condition)

    def parallel_retriever(self, query, condition):
        with ThreadPoolExecutor() as executor:
            # Schedule both tasks in parallel
            future_local = executor.submit(retrieve_local_relevant_sentences, query)
            future_web = executor.submit(self.web_retriever.web_crawler, query, condition)

            # Wait for both to complete
            local_results = future_local.result()
            web_results = future_web.result()
            # print(local_results)

        return local_results, web_results
    def merge_data(self, query, condition):
        local_results, web_results = self.parallel_retriever(query, condition)
        combined_result = local_results + web_results
        ranked=self.ranker.rank(query, combined_result)
        # print(ranked)
        return ranked


# Test it
if __name__ == "__main__":
    user_query = "I'm shaky, sweaty, and my sugar is 55 — what should I do?"
    Agg=DataAggregator()
    Agg.merge_data(user_query, "Diabetes")
    # print(results)
    # print("🔍 Top Local Matches:\n")
    # for i, r in enumerate(results, 1):
    #     print(f"{i}. ({r['id']}) {r['sentence']}\n")





