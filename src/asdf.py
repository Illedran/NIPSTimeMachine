"""
Author: Guillermo Alonso

In this module we will explore author clustering. Note that at first I will
be reading the data from the ``.csv`` files instead of the sqlite database.
"""
from collections import defaultdict
import csv
import numpy as np
import gensim
import pickle
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans

from papers import get_text_keywords_sanitized
from papers import build_models

# Key: author id. Value: Author name
author_names = {}

# Key: author id. Value: List of paper id's of that author
author_papers = defaultdict(lambda: [])

# Key: Paper id. Value: List of author id's who collaborated on that paper
paper_authors = defaultdict(lambda: [])

author_csv_count = 0


# TODO: Think about how we are obtaining the author_distributions.
# Probably, they come from a dictionary, so we need to somehow get the
# corresponding author_id for each author distribution, to later be able to
# retrieve who the fuck is that author.

# asdf.py

with open('author_distributions.pickle', 'rb') as handle:
    # author_distributions is a dictionary, in which the key is each
    # author_id, and the value is its distributions (a list of tuples, where
    # each tuple is (topic, topic_importance).
    author_distributions = pickle.load(handle)

print(len(author_distributions))

list_of_lists = []

for auth, dist in author_distributions.items():
    topic_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for topic, relevance in dist:
        topic_list[topic] = relevance

    list_of_lists.append(topic_list)

topic_relevance = np.array(list_of_lists)

def apply_kmeans(data, cluster_count=20, debug=True):
    if debug:
        print('Applying K-means with K = {} ...'.format(cluster_count))

    estimator = KMeans(n_clusters=cluster_count)
    kmeans = estimator.fit(topic_relevance)

    # if debug:
        # print('Centers for the centroids:')
        # print(kmeans.cluster_centers_)

    unique, counts = np.unique(kmeans.labels_, return_counts=True)
    if debug:
        print('Number of authors belonging to each cluster:',
              dict(zip(unique, counts)))
        print('Inertia: ', kmeans.inertia_)

    return kmeans

kmeans = apply_kmeans(topic_relevance, cluster_count=10)

print(kmeans.labels_)
"""
# Next steps
Take the different vectors for each author (topic grading schemes).

Since we have done the clustering, for finding similar authors, we scan the
authors in the same cluster and for all points in that cluster, calculate the
cosine through https://math.stackexchange.com/questions/53291/how-is-the-angle-between-2-vectors-in-more-than-3-dimensions-defined .
Then, select the top N closest ones, and return the name of the author.
"""









import numpy as np
from math import pi

def unit_vector(vector):
    """
    Returns the unit vector of the vector.
    """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """
    Returns the angle in degrees between two vectors represented as a tuple.
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)) * 180 / pi

print(angle_between((1, 0, 0), (-1, 0, 0)))