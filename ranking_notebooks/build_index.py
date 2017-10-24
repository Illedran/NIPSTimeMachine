# -*- coding: utf-8 -*-
__author__ = "Egor Lomagin"

import pickle
from sqlite3 import connect

from tqdm import tqdm

from preproc import Preprocessor
from ranking import BasicVSRanker, EnsembleRanker


def main():
    con = connect('nips-data/database.sqlite')

    texts = [x[0]
             for x in con.execute('SELECT paper_text FROM papers;').fetchall()]
    titles = [x[0]
              for x in con.execute('SELECT title FROM papers;').fetchall()]
    # years = con.execute('select year from papers;').fetchall()

    prepr = Preprocessor()

    texts_t = [prepr.process(text) for text in tqdm(texts)]
    titles_t = [prepr.process(title) for title in tqdm(titles)]

    text_r = BasicVSRanker.from_tokenized(texts_t)
    title_r = BasicVSRanker.from_tokenized(titles_t)

    ranker = EnsembleRanker()
    ranker.add_ranker(text_r, 0.9)
    ranker.add_ranker(title_r, 0.1)

    with open('models/ranker.pkl3', 'wb') as f:
        pickle.dump(ranker, f)


if __name__ == '__main__':
    main()
