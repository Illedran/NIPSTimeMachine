import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from preprocessing import Preprocessor


class BasicVSRanker:

    @staticmethod
    def from_tokenized(texts, prepr=Preprocessor()):
        vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=1000)
        vectorized_texts = vectorizer.fit_transform([" ".join(text) for text in texts])

        ranker = BasicVSRanker()
        ranker.vectorizer = vectorizer
        ranker.vectorized_texts = vectorized_texts
        ranker.prepr = prepr

        return ranker

    @staticmethod
    def from_raw(texts, prepr=Preprocessor()):
        tokenized = prepr.process_texts(texts)
        return BasicVSRanker.from_tokenized(tokenized)

    def best_n_matches(self, query, n=10):
        query = self.prepr.process(query)
        query = self.vectorizer.transform(query)
        return np.argsort(-cosine_similarity(query, self.vectorized_texts)).flatten()[:n]