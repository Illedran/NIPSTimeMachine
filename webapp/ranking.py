# -*- coding: utf-8 -*-
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from preprocessing import Preprocesser
from pathos.multiprocessing import Pool
import pandas as pd
import pickle


class BasicVSRanker:
    @classmethod
    def generate_default_ranker(cls):
        data = pd.read_csv('../nips-data/papers.csv')
        with open("models/ranker.pkl3", 'wb') as f:
            pickle.dump(cls(data.paper_text), f)

    @classmethod
    def generate_ranker(cls, texts):
        return cls(texts)

    def __init__(self, texts):
        vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=1000)
        with Pool() as executor:
            vectorized_texts = vectorizer.fit_transform(
                [" ".join(ptext) for ptext in executor.map(Preprocesser.process, texts)])

        self.vectorizer = vectorizer
        self.vectorized_texts = vectorized_texts
        self.similarity_function = cosine_similarity

    def get_best_matches(self, query, n=10):
        query = Preprocesser.process(query)
        query = self.vectorizer.transform([" ".join(query)])
        return np.argsort(
            -self.similarity_function(query, self.vectorized_texts)
        ).flatten()[:n]

    def get_scores(self, query):
        query = Preprocesser.process(query)
        query = self.vectorizer.transform([" ".join(query)])
        return self.similarity_function(query, self.vectorized_texts)
