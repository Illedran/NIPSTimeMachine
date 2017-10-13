# Author: Krists Kreics
import sys
import csv
import operator
import gensim
from collections import defaultdict
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
from stop_words import get_stop_words
from collections import OrderedDict

class Authors:
  # Check for numbers in text
  def is_number(n):
    try:
      float(n)
      return True
    except:
      return False


  def retrieve(self, name, db):
    sql_query = 'SELECT id, name FROM authors WHERE name LIKE "%' + name + '%";'
    results = db.execute(sql_query).fetchall()
    unique_authors = [r[1] for r in results]
    results = [r[0] for r in results]
    error_message = self.check_author_validity(set(unique_authors), name)
    if len(error_message) > 0:
      return error_message
    else:
      return results

  def check_author_validity(self, authors, name):
    # Make sure that only one author is matched.
    response = ''
    if len(authors) == 0:
      response = 'Could not find any author named "{}"'.format(name)
    if len(authors) > 1:
      potential_authors = ', '.join(authors)
      response = 'Different authors found. Did you mean one of these: ' + potential_authors

    return response

  def get_author_paper_ids(self, author_ids, db):
    # Retrieve relevant paper ids for the author
    sql_query = 'select paper_id from paper_authors where author_id in (' + ','.join((str(i) for i in author_ids)) + ')'
    paper_ids = db.execute(sql_query).fetchall()
    paper_ids = [p[0] for p in paper_ids]
    return paper_ids

  def get_relevant_papers(self, author_ids, db):
    # Retrieve papers of the author
    paper_ids = self.get_author_paper_ids(author_ids, db)
    sql_query = 'select id, title, year from papers where id in (' + ','.join((str(i) for i in paper_ids)) + ')'
    results = db.execute(sql_query).fetchall()
    results = {r[0] : r[1:] for r in results}

    return [results[i] for i in paper_ids]

  def get_coauthors(self, author_ids, db):
    # Get co-authors with collab count
    coauthors_with_count = {}
    coauthors = defaultdict(lambda: 0)
    paper_ids = self.get_author_paper_ids(author_ids, db)
    sql_query = 'select author_id from paper_authors where paper_id in (' + ','.join((str(i) for i in paper_ids)) + ')'
    results = db.execute(sql_query).fetchall()
    results = [r[0] for r in results]
    for cid in set(results):
        if results.count(cid) > 2: coauthors[cid] = results.count(cid)
    sql_query = 'select id, name from authors where id in (' + ','.join((str(i) for i in set(results))) + ')'
    results = db.execute(sql_query).fetchall()
    results = {r[0] : r[1] for r in results}
    for coauthor in coauthors:
        for r in results:
            if r == coauthor:
                coauthors_with_count[results[r]] = coauthors[coauthor]

    OrderedDict(sorted(coauthors_with_count.items(), key=operator.itemgetter(1), reverse=True))
    return OrderedDict(sorted(coauthors_with_count.items(), key=operator.itemgetter(1), reverse=True))

  def get_author_texts_and_years(relevant_papers):
    author_texts = []
    years = defaultdict(lambda: 0)

    with open('../nips-data/papers.csv', 'r') as csv_file:
      papers = csv.DictReader(csv_file)
      # Get paper-year allocation
      for paper in papers:
        for relevant_paper in relevant_papers:
          if paper.get('id') == relevant_paper:
            author_texts.append(paper.get('abstract'))
            year = paper.get('year')
            years[year] += 1

    return (author_texts, years)

  def get_text_keywords_sanitized(author_texts):
    texts = []
    tokenizer = RegexpTokenizer(r'\w+')
    en_stop = get_stop_words('en')

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

    return texts


  def build_models(texts):
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


  if __name__ == '__main__':

    relevant_authors, author_variety = process_authors(q)

    check_author_validity(author_variety, q)

    relevant_papers = get_relevant_papers(relevant_authors)

    coauthors = get_coauthors(relevant_papers, relevant_authors)

    sorted_coauthors = sorted(coauthors, key=operator.itemgetter(1), reverse=True)

    # Print some information
    print('List of common co-authors:')
    with open('../nips-data/authors.csv', 'r') as csv_file:
      authors = csv.DictReader(csv_file)
      for author in authors:
        for coauthor in sorted_coauthors[:5]:
          if author.get('id') == coauthor:
            print(author.get('name'))

    author_texts, years = get_author_texts_and_years(relevant_papers)

    # Print some information
    sorted_years = sorted(years)
    print('Count of papers by year:')
    for year in range(int(sorted_years[0]), int(sorted_years[-1])):
      year_str = str(year)
      if year_str in years:
        print(year_str + ': ' + str(years[year_str]))

    texts = get_text_keywords_sanitized(author_texts)

    build_models(texts)
