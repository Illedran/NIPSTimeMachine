# Author: Krists Kreics
import operator
from collections import defaultdict, OrderedDict
from preprocessing import Preprocessor
import gensim

# Check for numbers in text
def is_number(n):
    try:
        float(n)
        return True
    except:
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
        sql_query = 'select * from papers where id in (' + ','.join((str(i) for i in paper_ids)) + ')'
        results = db.execute(sql_query).fetchall()
        results = {r[0] : r[1:] for r in results}

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
        sql_query = 'select author_id from paper_authors where paper_id in (' + ','.join((str(i) for i in paper_ids)) + ')'
        results = db.execute(sql_query).fetchall()
        results = [r[0] for r in results]
        for cid in set(results):
            if results.count(cid) > 2 and cid not in author_ids: coauthors[cid] = results.count(cid)

        return (coauthors, set(results))

    def get_coauthors(self, author_ids, db):
        # Get co-authors with collab count
        coauthors_with_count = {}
        coauthors, coauthor_ids = self.get_coauthor_ids(author_ids, db)
        sql_query = 'select id, name from authors where id in (' + ','.join((str(i) for i in coauthor_ids)) + ')'
        results = db.execute(sql_query).fetchall()
        results = {r[0] : r[1] for r in results}
        for coauthor in coauthors:
            for r in results:
                if r == coauthor: coauthors_with_count[results[r]] = coauthors[coauthor]

        return OrderedDict(sorted(coauthors_with_count.items(), key=operator.itemgetter(1), reverse=True))

    def get_years(self, author_ids, db):
        years = defaultdict(lambda: 0)
        papers = self.get_relevant_papers(author_ids, db)
        for p in papers:
            years[p[0]] += 1

        return OrderedDict(sorted(years.items(), key=operator.itemgetter(0)))

    def get_text_tokens(self, author_texts):
        texts = []
        results = []
        preprocessor = Preprocessor()
        texts = preprocessor.process_texts(author_texts)
        for tokens in texts:
            terms = filter(lambda x: len(x) > 2 and not is_number(x), tokens)
            results.append(list(terms))

        return results

    def get_keywords(self, author_ids, db):
        papers_text = self.get_author_texts(author_ids, db)

        return gensim.summarization.keywords(papers_text, ratio=0.05).split('\n')
