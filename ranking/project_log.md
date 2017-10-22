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

**Deliverables**
Basic vector space retreival ranking implementation with TF-IDF features.
- Python module for text preprocessing: tokenization, stemming (with ability to choose different parameters and strategies).
- Python module for (d, q) pair scoring.
- Jupyter Notebook for module demonstration.

### Weighted VSR zone ranking
**Directory:** 3_vsr_zones

**Deliverables**
Implementation of VSR ranking with zone weights.
- Python module for (d, q) pair scoring.
- Jupyter Notebook for module demonstration.

### Similarity punishment
**Directory:** 4_sim_punishment

**Deliverables**
Algorithm for score punishment of near-duplicates in the retreival list.
- Jupyter notebook with different possible implementations.
- Modification of ranking module.

### Automated zone-weight infering

**Directory:** 5_zone_weight_learning

**Deliverables**
Algorithm for automated calculation of zone-weights based on user response.
- Jupyter Notebook with implementation.
- Modification of ranking module.