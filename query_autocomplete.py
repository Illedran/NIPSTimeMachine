from collections import defaultdict, Counter
from preproc import Preprocessor, NoStemmer
from tqdm import tqdm
import re
import pickle
from sqlite3 import connect


def _build_from_corpus():
    con = connect('./nips-data/database.sqlite')
    prepr = Preprocessor()
    prepr.stemmer = NoStemmer()
    titles = [x[0] for x in con.execute('select title from papers;')]
    titles_t = [list(prepr.process(title)) for title in tqdm(titles)]
    d = defaultdict(Counter)
    for title in tqdm(titles_t):
        l = len(title)
        for i in range(0, l-2):
            d[title[i]].update(title[i+1:i+2 + 1])
    final = {}
    for k, v in d.items():
        final[k] = [x[0] for x in v.most_common(10)]

    return final


class QueryAutocomplete:

    def __init__(self):
        self.prepr = Preprocessor()
        self.complete_dict = _build_from_corpus()
        self.last_word_regex = re.compile(r'\b([a-z]{2,})$')

    def complete(self, query):
        last_word = self.last_word_regex.findall(query)
        if last_word:
            last_word = last_word[0]
        else:
            return []
        if last_word in self.complete_dict:
            return self.complete_dict[last_word]
        else:
            return []


def main():
    qa = QueryAutocomplete()
    with open('models/autocomplete.pkl3', 'wb') as f:
        pickle.dump(qa, f)

if __name__ == '__main__':
    main()
