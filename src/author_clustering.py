"""
Author: Guillermo Alonso

In this module we will explore author clustering. Note that at first I will
be reading the data from the ``.csv`` files instead of the sqlite database.
"""
from collections import defaultdict
import csv
import numpy as np

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

# Fill the author_names dictionary
with open('../nips-data/authors.csv', 'r') as csv_file:
    auth_reader = csv.DictReader(csv_file, delimiter=',')
    for author in auth_reader:
        author_csv_count += 1
        author_names[author['id']] = author['name']

# Check data validity
assert len(author_names) == author_csv_count
print('The total number of authors is', author_csv_count)

# Fill the author_papers dictionary
with open('../nips-data/paper_authors.csv', 'r') as csv_file:
    paper_reader = csv.DictReader(csv_file, delimiter=',')
    for paper in paper_reader:
        author_papers[paper['author_id']].append(paper['paper_id'])
        paper_authors[paper['paper_id']].append(paper['author_id'])

# Check data validity
assert len(author_names) == len(author_papers)

print('Internal dictionaries filled OK')

print('Let us take a look at some information from the dataset')
paper_lengths = [len(papers) for papers in author_papers.values()]
print('The minimum number of papers by an author is:', min(paper_lengths))
print('The maximum number of papers by an author is:', max(paper_lengths))
print('The average number of papers of the authors is:',
      sum(paper_lengths)/len(paper_lengths))


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

author_texts = get_author_texts(paper_authors)

print('Author texts extracted successfully')

for author, author_texts in author_texts.values():
    sanitized = get_text_keywords_sanitized(author_texts)
    build_models(sanitized, savefile_prefix=int(author))
