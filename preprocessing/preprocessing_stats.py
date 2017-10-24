# -*- coding: utf-8 -*-
import re

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from fuzzywuzzy import fuzz

from preprocessing import Preprocesser

data = pd.read_csv('nips-data/papers.csv')
abstract_cleaner = re.compile(r'(- \n)|(\n)')

abstracts1 = data.paper_text.apply(Preprocesser.extract_abstract)

abstracts2 = data.abstract.apply(
    lambda abstr: re.sub(abstract_cleaner, '', abstr).strip())

res = []
for fuzz_ratio in range(0,101):
    count = 0
    match = 0
    for i in range(len(abstracts1)):
        if abstracts2.iloc[i] != 'Abstract Missing':
            count += 1
            if fuzz.ratio(abstracts2.iloc[i], abstracts1.iloc[i]) >= fuzz_ratio:
                match += 1
    res.append((fuzz_ratio, match/count))

x, y = zip(*res)

x = list(map(lambda el: el*0.01, x))
y = list(map(lambda el: el*count, y))

plt.plot(x, y)
plt.title("Number of matching abstracts (y) that have ratio greater than (x)")
plt.xlabel("ratio(a,b)")
plt.ylabel("Number of matching abstracts")
matplotlib.rcParams.update({'font.size': 22})

plt.show()