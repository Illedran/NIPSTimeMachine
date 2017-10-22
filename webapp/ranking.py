import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
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

    def get_scores(self, query):
        query = self.process_query(query)
        return self.similarity_function(query, self.vectorized_texts)

    def get_best_matches(self, query, n=10):
        scores = self.get_scores(query)
        return np.argsort(-scores).flatten()[:n]


class EnsembleRanker:

    def __init__(self):
        self.rankers = []
        self.weights = []

    def add_ranker(self, ranker, weight):
        self.rankers.append(ranker)
        self.weights.append(weight)

    def get_scores(self, query):
        scores = []
        for r, w in zip(self.rankers, self.weights):
            scores.append(r.get_scores(query) * w)
        return sum(scores)

    def get_best_matches(self, query, n=10):
        scores = self.get_scores(query)
        return np.argsort(-scores).flatten()[:n]
