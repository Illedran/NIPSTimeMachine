# Author: Krists Kreics
import sys
import csv
import operator
import gensim
from collections import defaultdict
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
from stop_words import get_stop_words

# Check for numbers in text
def is_number(n):
  try:
    float(n)
    return True
  except:
    return False

def get_texts():
  texts = []

  with open('../nips-data/papers.csv', 'r') as csv_file:
    papers = csv.DictReader(csv_file)
    # Get paper-year allocation
    for paper in papers:
      texts.append(paper.get('paper_text'))

  return texts

def get_text_keywords_sanitized(all_texts):
  texts = []
  tokenizer = RegexpTokenizer(r'\w+')
  en_stop = get_stop_words('en')

  # LDA topic extraction
  # Remove stop words and stem
  for text in all_texts:
    raw = text.lower()
    tokens = tokenizer.tokenize(raw)
    stopped_tokens = [i for i in tokens if not i in en_stop]
    p_stemmer = PorterStemmer()
    stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens]
    terms = filter(lambda x: len(x) > 2 and not is_number(x), stopped_tokens)
    texts.append(list(terms))

  return texts


def build_models(texts):
  topics = 10
  passes = 5
  # Build models
  dictionary = gensim.corpora.Dictionary(texts)
  corpus = [dictionary.doc2bow(text) for text in texts]
  ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=topics, id2word=dictionary, passes=passes)

  dictionary.save('topics.dict')
  gensim.corpora.MmCorpus.serialize('topics.mm', corpus)
  ldamodel.save('topics.lda')

  # Print results of topic modeling
  print('LDA:')
  print(ldamodel.show_topics(10, 7))


if __name__ == '__main__':

  all_texts = get_texts()

  texts = get_text_keywords_sanitized(all_texts)

  build_models(texts)
