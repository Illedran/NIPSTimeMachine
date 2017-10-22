# Ranking/scoring system for NIPS dataset entities

## Project description
The goal of this project is to create ranking/scoring system for NIPS dataset entities and to integrate it into NIPS IR system developed in group. Given the search query this system should improve quality of search results i.e.:

* make more valuable entries appear first in search result list;
* increase diversity of first entries of search result list.

## Tasks

### NIPS dataset exploration
**Directory:** 1_nips_exploration

**Input:** corpus of articles from NIPS conference. Year of publication, authors, title and abstract.

**Deliverables**
Set of documents providing basic information about dataset.
Article count, author count, unique word count, most frequent words, count of articles by year distribution, missing values, article size distribution, authors with most publications, articles with most authors, author cowork graph, basic topic modeling.

### VSR baseline
**Directory:** 2_vsr_baseline

**Input:** NIPS dataset

**Deliverables**
Basic vector space retreival ranking implementation with TF-IDF features.
- Python module for text preprocessing: tokenization, stemming (with ability to choose different parameters and strategies).
- Python module for (d, q) pair scoring.
- Jupyter Notebook for module demonstration.
