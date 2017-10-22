import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from preprocessing import Preprocessor


class BasicVSRanker:

    @staticmethod
    def from_tokenized(texts, prepr=Preprocessor()):
        vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=1000)
        vectorized_texts = vectorizer.fit_transform(
            [" ".join(text) for text in texts])

        ranker = BasicVSRanker()
        ranker.vectorizer = vectorizer
        ranker.vectorized_texts = vectorized_texts
        ranker.prepr = prepr
        ranker.query_prepr = prepr
        ranker.similarity_function = cosine_similarity

        return ranker

    @staticmethod
    def from_raw(texts, prepr=Preprocessor()):
        tokenized = prepr.process_texts(texts)
        return BasicVSRanker.from_tokenized(tokenized, prepr)

    def process_query(self, query):
        query = self.query_prepr.process(query)
        query = self.vectorizer.transform([" ".join(query)])
        return query

    def get_best_matches(self, query, n=10):
        query = self.process_query(query)
        return np.argsort(
            -self.similarity_function(query, self.vectorized_texts)
        ).flatten()[:n]

    def get_scores(self, query):
        query = self.process_query(query)
        return self.similarity_function(query, self.vectorized_texts)


class ZoneVSRRanker:

    def __init__(self):
        self.zones = {}

    def add_zone_text(self, texts, prepr=Preprocessor()):
        ranker = BasicVSRanker.from_raw(texts, prepr)
        self.zones.append(ranker)

    def add_zone_tokenized(self, tokenized):
        ranker = BasicVSRanker.from_raw(texts, prepr)
        self.zones.append(ranker)
