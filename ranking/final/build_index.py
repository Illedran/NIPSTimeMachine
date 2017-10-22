import numpy as np
import pandas as pd
from tqdm import tqdm
from sqlite3 import connect
from preprocessing import Preprocessor
from ranking import BasicVSRanker, EnsembleRanker


def main():
    con = connect('../data/nips-papers/database.sqlite')

    texts = [x[0]
             for x in con.execute('select paper_text from papers;').fetchall()]
    titles = [x[0]
              for x in con.execute('select title from papers;').fetchall()]
    years = con.execute('select year from papers;').fetchall()

    prepr = Preprocessor()

    texts_t = [prepr.process(text) for text in tqdm(texts)]
    titles_t = [prepr.process(title) for title in tqdm(titles)]
    
    text_r = BasicVSRanker.from_tokenized(texts_t)
    title_r = BasicVSRanker.from_tokenized(titles_t)

    ranker = EnsembleRanker()
    ranker.add_ranker(text_r, 0.9)
    ranker.add_ranker(title_r, 0.1)

    with open('ranker.pkl3', 'wb') as f:
        pickle.dump(ranker, f)


if __name__ == '__main__':
    main()