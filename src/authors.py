# Author: Krists Kreics
import sys
import csv
import operator

q = 'Michael I. Jordan'

author_variety = []
relevant_authors = []
relevant_papers = []

coauthors = {}
years = {}

papers = csv.DictReader(open('../nips-data/papers.csv'))
authors = csv.DictReader(open('../nips-data/authors.csv'))
paper_authors = csv.DictReader(open('../nips-data/paper_authors.csv'))

# Get all authors that have a similar name
for author in authors:
  if author.get('name').find(q) != -1:
    relevant_authors.append(author.get('id'))
    author_variety.append(author.get('name'))

# We have to narrow it down to just one author
unique_authors = list(set(author_variety))
if (len(unique_authors) != 1):
  potential_authors = ', '.join(unique_authors)
  sys.exit('Did you mean one of these: ' + potential_authors)

for relevant_author in relevant_authors:
  for paper_author in paper_authors:
    if paper_author.get('author_id') == str(relevant_author):
      relevant_papers.append(paper_author.get('paper_id'))

paper_authors = csv.DictReader(open('../nips-data/paper_authors.csv'))

# Get co-authors
for paper_author in paper_authors:
  for relevant_paper in relevant_papers:
    if str(relevant_paper) == paper_author.get('paper_id'):
      if paper_author.get('author_id') not in relevant_authors:
        author = paper_author.get('author_id')
        if author in coauthors:
          coauthors[author] +=1
        else:
          coauthors[author] = 1

sorted_coauthors = sorted(coauthors, key=operator.itemgetter(1), reverse=True)
authors = csv.DictReader(open('../nips-data/authors.csv'))

print('List of common co-authors:')

for author in authors:
  for coauthor in sorted_coauthors[:5]:
    if author.get('id') == coauthor: print(author.get('name'))

# Get paper-year allocation
for paper in papers:
  for relevant_paper in relevant_papers:
    if paper.get('id') == relevant_paper:
      year = paper.get('year')
      if year in years:
        years[year] += 1
      else:
        years[year] = 1

sorted_years = sorted(years, key=operator.itemgetter(1))

print('Count of papers by year:')

for year in range(int(sorted_years[-1]), int(sorted_years[0])):
  year_str = str(year)
  if year_str in years:
    print(year_str + ': ' + str(years[year_str]))
