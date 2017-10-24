# -*- coding: utf-8 -*-
__author__ = "Krists Kreics"

import operator
import pickle
from collections import defaultdict, OrderedDict

import gensim

from preproc import Preprocessing


# Check for numbers in text
def is_number(n):
    try:
        float(n)
        return True
    except ValueError:
        return False


class Authors:
    def retrieve(self, name, db):
        sql_query = 'SELECT id, name FROM authors WHERE name LIKE "%' + name + '%";'
        results = db.execute(sql_query).fetchall()
        unique_authors = [r[1] for r in results]
        results = [r[0] for r in results]
        error_message = self.check_author_validity(set(unique_authors), name)

        return error_message if len(error_message) > 0 else results

    def check_author_validity(self, authors, name):
        # Make sure that only one author is matched.
        response = ''
        if len(authors) == 0:
            response = 'Could not find any author named "{}"'.format(name)
        elif len(authors) <= 10 and len(authors) > 1:
            potential_authors = ', '.join(authors)
            response = 'Different authors found. Did you mean one of these: ' + potential_authors
        elif len(authors) > 10:
            potential_authors = ', '.join(list(authors)[:10] + ['...'])
            response = 'Different authors found. Did you mean one of these: ' + potential_authors

        return response

    def get_author_paper_ids(self, author_ids, db):
        # Retrieve relevant paper ids for the author
        sql_query = 'SELECT paper_id FROM paper_authors WHERE author_id IN (' + ','.join(
            (str(i) for i in author_ids)) + ')'
        paper_ids = db.execute(sql_query).fetchall()
        paper_ids = [p[0] for p in paper_ids]

        return paper_ids

    def get_relevant_papers(self, author_ids, db):
        # Retrieve papers of the author
        paper_ids = self.get_author_paper_ids(author_ids, db)
        sql_query = 'SELECT * FROM papers WHERE id IN (' + ','.join(
            (str(i) for i in paper_ids)) + ')'
        results = db.execute(sql_query).fetchall()
        results = {r[0]: r[1:] for r in results}

        return [results[i] for i in paper_ids]

    def get_author_texts(self, author_ids, db):
        papers_text = ''
        papers = self.get_relevant_papers(author_ids, db)
        for paper in papers:
            papers_text += paper[1]

        return papers_text

    def get_coauthor_ids(self, author_ids, db):
        coauthors = defaultdict(lambda: 0)
        paper_ids = self.get_author_paper_ids(author_ids, db)
        sql_query = 'SELECT author_id FROM paper_authors WHERE paper_id IN (' + ','.join(
            (str(i) for i in paper_ids)) + ')'
        results = db.execute(sql_query).fetchall()
        results = [r[0] for r in results]
        for cid in set(results):
            if results.count(cid) > 2 and cid not in author_ids: coauthors[
                cid] = results.count(cid)

        return (coauthors, set(results))

    def get_coauthors(self, author_ids, db):
        # Get co-authors with collab count
        coauthors_with_count = {}
        coauthors, coauthor_ids = self.get_coauthor_ids(author_ids, db)
        sql_query = 'SELECT id, name FROM authors WHERE id IN (' + ','.join(
            (str(i) for i in coauthor_ids)) + ')'
        results = db.execute(sql_query).fetchall()
        results = {r[0]: r[1] for r in results}
        for coauthor in coauthors:
            for r in results:
                if r == coauthor: coauthors_with_count[results[r]] = coauthors[
                    coauthor]

        return OrderedDict(
            sorted(coauthors_with_count.items(), key=operator.itemgetter(1),
                   reverse=True))

    def get_years(self, author_ids, db):
        years = defaultdict(lambda: 0)
        papers = self.get_relevant_papers(author_ids, db)
        for p in papers:
            years[p[0]] += 1

        return OrderedDict(sorted(years.items(), key=operator.itemgetter(0)))

    def get_text_tokens(self, author_texts):
        results = []
        texts = Preprocessing.process(author_texts)
        for tokens in texts:
            terms = filter(lambda x: len(x) > 2 and not is_number(x), tokens)
            results.append(list(terms))

        return results

    def get_keywords(self, author_ids, db):
        papers_text = self.get_author_texts(author_ids, db)

        return gensim.summarization.keywords(papers_text, ratio=0.75).split(
            '\n')

    def get_topics(self, author_ids, db):
        top_topics = []
        papers_text = self.get_author_texts(author_ids, db)
        dictionary = gensim.corpora.Dictionary.load('./models/topics.dict')
        corpus = gensim.corpora.MmCorpus('./models/topics.mm')
        query = dictionary.doc2bow(papers_text.lower().split())
        lda = gensim.models.ldamodel.LdaModel.load('./models/topics.lda')
        topics = lda[query]
        a = list(sorted(topics, key=lambda x: x[1]))
        for i in range(min(len(a), 3)):
            top_topics.append(lda.print_topic(a[i][0]))

        return top_topics

    def get_similar_paper_ids(self, author_ids, db):
        similar_paper_ids = []
        paper_ids = self.get_author_paper_ids(author_ids, db)
        papers = self.get_relevant_papers(author_ids, db)
        dictionary = gensim.corpora.Dictionary.load('./models/topics.dict')
        corpus = gensim.corpora.MmCorpus('./models/topics.mm')
        lda = gensim.models.ldamodel.LdaModel.load('./models/topics.lda')
        similarity = gensim.similarities.MatrixSimilarity.load(
            './models/similar_topics.index')
        similar_cut = len(paper_ids) + 1
        for paper in papers:
            query = dictionary.doc2bow(paper[5].lower().split())
            topics = lda[query]
            s = similarity[topics]
            s = sorted(enumerate(s), key=lambda item: -item[1])
            s = s[:similar_cut]
            for p in s:
                if p[0] not in paper_ids:
                    similar_paper_ids.append(p[0])
                    break

        return similar_paper_ids[:10]

    def get_similar_papers(self, author_ids, db):
        similar_paper_ids = self.get_similar_paper_ids(author_ids, db)
        sql_query = 'SELECT title, year FROM papers WHERE id IN (' + ','.join(
            (str(i) for i in similar_paper_ids)) + ')'
        similar_papers = db.execute(sql_query).fetchall()
        similar_papers = {similar_paper[0]: similar_paper[1] for similar_paper
                          in similar_papers}

        return similar_papers

    def get_similar_authors(self, author_ids, db):
        similar_paper_ids = self.get_similar_paper_ids(author_ids, db)
        sql_query = 'SELECT author_id FROM paper_authors WHERE paper_id IN (' + ','.join(
            (str(i) for i in similar_paper_ids)) + ')'
        results = db.execute(sql_query).fetchall()
        results = [r[0] for r in results]
        sql_query = 'SELECT name FROM authors WHERE id IN (' + ','.join(
            (str(i) for i in results[:10])) + ');'
        similar_authors = db.execute(sql_query).fetchall()
        similar_authors = [similar_author[0] for similar_author in
                           similar_authors]

        return similar_authors

    def get_citation_rating(self, author_ids, db):
        file = open('models/bindex.p', 'rb')
        rating = 0
        index = pickle.load(file)
        results = []
        papers = self.get_relevant_papers(author_ids, db)
        for paper in papers:
            useful = []
            citations = []
            stopped_tokens = list(Preprocessing.process_bindex(paper[1]))
            for i in range(len(stopped_tokens) - 1):
                biword = stopped_tokens[i] + ' ' + stopped_tokens[i + 1]
                if biword in index: useful.append(index[biword])
            for i in range(len(useful) - 1):
                citations = list(set(useful[i]) & set(useful[i + 1]))
            if len(citations) > 0: results.append(len(citations))
        results = sorted(results)
        if len(results) > 0:
            for r in range(max(results)):
                if len(list(filter(lambda x: x >= r, results))) >= r: rating = r

        return rating
