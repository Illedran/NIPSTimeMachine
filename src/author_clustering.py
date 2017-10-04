"""
Author: Guillermo Alonso

In this module we will explore author clustering. Note that at first I will
be reading the data from the ``.csv`` files instead of the sqlite database.

It is assumed that the ``.csv`` files exist within the same folder than this
script.
"""
from collections import defaultdict

import csv

# Key: author id. Value: Author name
author_names = {}

# Key: author id. Value: List of paper id's of that author
author_papers = defaultdict(lambda: [])

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

# Check data validity
assert len(author_names) == len(author_papers)

print('Dictionaries filled OK')

print('Let us take a look at some information from the dataset')
paper_lengths = [len(papers) for papers in author_papers.values()]
print('The minimum number of papers by an author is:', min(paper_lengths))
print('The maximum number of papers by an author is:', max(paper_lengths))
print('The average number of papers of the authors is:',
      sum(paper_lengths)/len(paper_lengths))
