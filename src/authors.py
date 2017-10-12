# Author: Krists Kreics
import sys
import csv
import operator
import gensim
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
from stop_words import get_stop_words

tokenizer = RegexpTokenizer(r'\w+')
en_stop = get_stop_words('en')
q = 'Michael I. Jordan'

author_texts = []
author_variety = []
relevant_authors = []
relevant_papers = []
texts = []

coauthors = {}
years = {}

# Check for numbers in text
def is_number(n):
  try:
    float(n)
    return True
  except:
    return False

# Get all authors that have a similar name

with open('../nips-data/authors.csv', 'r') as csv_file:
  authors = csv.DictReader(csv_file)
  for author in authors:
    if author.get('name').find(q) != -1:
      relevant_authors.append(author.get('id'))
      author_variety.append(author.get('name'))

# We have to narrow it down to just one author
unique_authors = list(set(author_variety))

if len(unique_authors) == 0:
  sys.exit('Could not find any author named "{}"'.format(q))
if len(unique_authors) > 1:
  potential_authors = ', '.join(unique_authors)
  sys.exit('Different authors found. Did you mean one of these: ' + potential_authors)

for relevant_author in relevant_authors:
  with open('../nips-data/paper_authors.csv', 'r') as csv_file:
    paper_authors = csv.DictReader(csv_file)
    for paper_author in paper_authors:
      if paper_author.get('author_id') == str(relevant_author):
        relevant_papers.append(paper_author.get('paper_id'))


# Get co-authors
with open('../nips-data/paper_authors.csv', 'r') as csv_file:
  paper_authors = csv.DictReader(csv_file)
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

print('List of common co-authors:')

with open('../nips-data/authors.csv', 'r') as csv_file:
  authors = csv.DictReader(csv_file)
  for author in authors:
    for coauthor in sorted_coauthors[:5]:
      if author.get('id') == coauthor: print(author.get('name'))


with open('../nips-data/papers.csv', 'r') as csv_file:
  papers = csv.DictReader(csv_file)
  # Get paper-year allocation
  for paper in papers:
    for relevant_paper in relevant_papers:
      if paper.get('id') == relevant_paper:
        author_texts.append(paper.get('abstract'))
        year = paper.get('year')
        if year in years:
          years[year] += 1
        else:
          years[year] = 1

sorted_years = sorted(years)

print('Count of papers by year:')

for year in range(int(sorted_years[0]), int(sorted_years[-1])):
  year_str = str(year)
  if year_str in years:
    print(year_str + ': ' + str(years[year_str]))

# LDA topic extraction
# Remove stop words and stem
for text in author_texts:
  raw = text.lower()
  tokens = tokenizer.tokenize(raw)
  stopped_tokens = [i for i in tokens if not i in en_stop]
  # p_stemmer = PorterStemmer()
  # stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens]
  terms = filter(lambda x: len(x) > 2 and not is_number(x), stopped_tokens)
  texts.append(list(terms))

# Build models
dictionary = gensim.corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]
ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=5, id2word=dictionary, passes=20)
lsimodel = gensim.models.lsimodel.LsiModel(corpus, id2word=dictionary, num_topics=5)

# Print results of topic modeling
print('LDA:')
print(ldamodel.show_topics(10, 7))
print('LSI:')
print(lsimodel.print_topics(5))
