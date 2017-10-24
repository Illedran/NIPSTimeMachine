# -*- coding: utf-8 -*-
__author__ = "Guillermo Alonso"
"""
In this module we will explore author clustering. Note that at first I will
be reading the data from the ``.csv`` files instead of the sqlite database.
"""

import csv
import os
import pickle
import sys
from collections import defaultdict
from math import pi

import gensim
import numpy as np
from sklearn.cluster import KMeans


def get_author_texts(paper_authors):
    """
    Parameters
    ----------
    Dictionary, where:
        key: Paper ID.
        value: List of all authors who collaborated on that paper.

    Returns
    -------
    Dictionary, where:
        key: Author ID.
        value: List with all the papers content of that author.
    """
    texts = defaultdict(lambda: [])

    with open('../nips-data/papers.csv', 'r') as csv_file:
        papers = csv.DictReader(csv_file)
        # Get paper-year allocation
        for paper in papers:
            paper_id = paper.get('id')
            paper_text = paper.get('paper_text')
            authors = paper_authors[paper_id]
            for author in authors:
                texts[author].append(paper_text)

    return texts


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


def apply_kmeans(data, cluster_count=20, debug=True):
    if debug:
        print('Applying K-means with K = {} ...'.format(cluster_count))

    estimator = KMeans(n_clusters=cluster_count)
    kmeans = estimator.fit(data)

    unique, counts = np.unique(kmeans.labels_, return_counts=True)
    if debug:
        print('Number of authors belonging to each cluster:',
              dict(zip(unique, counts)))
        print('Inertia: ', kmeans.inertia_)

    return kmeans


def calculate_angle_of_author(author_id, author_names, list_of_lists):
    # There are two choices: pass an author id, or pass an author name
    if isinstance(author_id, int):
        author_name = author_names[str(author_id)]
        string_key = str(author_id)
        int_key = author_id
    if isinstance(author_id, str):
        author_name = author_id
        string_key = author_names[author_id]
        int_key = int(string_key)
    # TODO: change everything so that this shit works
    print('Calculating similar authors to:', author_name)
    a, b, c = None, None, None
    L = []
    # First, find the author
    for other_id, vector, cluster in list_of_lists:
        if str(other_id) == string_key:
            a, b, c = other_id, vector, cluster
            break

    for other_id, vector, cluster in list_of_lists:
        if str(other_id) == str(a) or cluster != c:
            continue

        angle = angle_between(b, vector)
        L.append([other_id, angle])

    for el in L:
        el[0] = author_names[el[0]]

    return sorted(L, key=lambda x: x[1])


def get_similar_authors(author_number):
    # Key: author id. Value: Author name
    author_names = {}

    # Key: author id. Value: List of paper id's of that author
    author_papers = defaultdict(lambda: [])

    # Key: Paper id. Value: List of author id's who collaborated on that paper
    paper_authors = defaultdict(lambda: [])

    # Fill the author_names dictionary
    with open('../nips-data/authors.csv', 'r') as csv_file:
        auth_reader = csv.DictReader(csv_file, delimiter=',')
        for author in auth_reader:
            author_names[author['id']] = author['name']
            author_names[author['name']] = author['id']

    # Fill the author_papers dictionary
    with open('../nips-data/paper_authors.csv', 'r') as csv_file:
        paper_reader = csv.DictReader(csv_file, delimiter=',')
        for paper in paper_reader:
            author_papers[paper['author_id']].append(paper['paper_id'])
            paper_authors[paper['paper_id']].append(paper['author_id'])

    print('Internal dictionaries filled OK')

    print('Let us take a look at some information from the dataset')
    paper_lengths = [len(papers) for papers in author_papers.values()]
    print('The minimum number of papers by an author is:', min(paper_lengths))
    print('The maximum number of papers by an author is:', max(paper_lengths))
    print('The average number of papers of the authors is:',
          sum(paper_lengths) / len(paper_lengths))

    # Construct a ndarray. For that, we need a list of lists, so that each sublists
    # represent the information of each author (as of now, only the number of
    # papers)
    np_array_lengths = np.array([[length] for length in paper_lengths])

    CLUSTER_COUNT = 4

    print('Applying K-means with K = {} ...'.format(CLUSTER_COUNT))

    estimator = KMeans(n_clusters=CLUSTER_COUNT)
    kmeans = estimator.fit(np_array_lengths)

    print('Centers for the centroids:')
    print(kmeans.cluster_centers_)

    unique, counts = np.unique(kmeans.labels_, return_counts=True)
    print('Number of authors belonging to each cluster:',
          dict(zip(unique, counts)))

    _author_texts = get_author_texts(paper_authors)

    # Load the model
    if not os.path.isfile('topics.dict') or not os.path.isfile('topics.lda'):
        sys.exit('Could not find model files (topics.dict and topics.lda)')

    dictionary = gensim.corpora.Dictionary.load('topics.dict')
    lda = gensim.models.ldamodel.LdaModel.load('topics.lda')
    print('Model loaded successfully')

    # If the author distributions is not present, we need to create it
    if not os.path.isfile('author_distributions.pickle'):
        author_distributions = {}

        for author, author_texts in _author_texts.items():
            query = dictionary.doc2bow(' '.join(author_texts).lower().split())
            author_distributions[author] = lda[query]

        print('Finished generating the distributions',
              len(author_distributions))
        with open('author_distributions.pickle', 'wb') as handle:
            pickle.dump(author_distributions, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)

    with open('author_distributions.pickle', 'rb') as handle:
        author_distributions = pickle.load(handle)

    print('Length of author distribution:', len(author_distributions))

    list_of_lists = []

    for auth, dist in author_distributions.items():
        topic_list = [auth, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        for topic, relevance in dist:
            topic_list[1][topic] = relevance

        list_of_lists.append(topic_list)

    relevances = []
    for a, b in list_of_lists:
        relevances.append(b)
    topic_relevance = np.array(relevances)

    kmeans = apply_kmeans(topic_relevance, cluster_count=10)

    print(kmeans.labels_)

    # Add to each author its cluster
    for i in range(len(list_of_lists)):
        list_of_lists[i].append(kmeans.labels_[i])

    # 330 michael jordan
    # 34 the one I was trying
    # 6338 the other michael jordan
    # author_number = "Michael I. Jordan"
    print('List of lists info:', type(list_of_lists), len(list_of_lists),
          list_of_lists[0])

    similar_authors = calculate_angle_of_author(author_number, author_names,
                                                list_of_lists)

    # Print the results
    print('Showing top 10 results (Author name, angle):')
    for i in range(10):
        print(similar_authors[i])

    return similar_authors


if __name__ == '__main__':
    get_similar_authors('Michael I. Jordan')
