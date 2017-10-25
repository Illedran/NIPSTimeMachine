# -*- coding: utf-8 -*-
__author__ = "Andrea Nardelli, Egor Lomagin"

from sqlite3 import connect

from flask import Flask, render_template, request, g

import construct_index
from authors import Authors
from authors import MultipleAuthorsFoundException, NoAuthorsFoundException
from engine import BasicEngine
from qbe import get_pdf_text_simple
from query_extractor import QueryExtractor, Author

app = Flask(__name__)
app.debug = True
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db_path = 'nips-data/database.sqlite'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect(db_path)
    return db


def get_engine():
    engine = getattr(g, '_engine', None)
    if engine is None:
        engine = g._engine = BasicEngine()
    return engine


def get_authors():
    authors = getattr(g, '_authors', None)
    if authors is None:
        authors = g._authors = Authors()
    return authors


def get_query_extractor():
    qe = getattr(g, '_query_extractor', None)
    if qe is None:
        db = get_db()
        qe = g._query_extractor = QueryExtractor(db)
    return qe


@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def retrieve_results_1(query, n=10, author_names=[], years=[]):
    try:
        results = construct_index.search(
            query, search_field="paper_text", index_name="index_with_content")
    except:
        return retrieve_results_2(query, n)

    engine = get_engine()
    scores = engine.ranker.get_scores(query).flatten()
    inv_ids = {v: k for k, v in enumerate(engine.ids_map)}

    new_res = []
    db = get_db()

    for i in range(results.scored_length()):
        j = int(results[i]['id'])
        authors = set([x[0].lower() for x in db.execute('''select name from authors
                join paper_authors on authors.id = author_id
                where paper_id = ?;''', [j]).fetchall()])
        new_res.append({
            'id': results[i]['id'],
            'title': results[i]['title'],
            'year': results[i]['year'],
            'authors': authors,
            'paper_text': results[i]['paper_text'],
            'snippets': results[i].highlights("paper_text"),
            'score': scores[inv_ids[j]],
        })

    for name in author_names:
        for res in new_res:
            if name in res['authors']:
                res['score'] += 0.25

    for year in years:
        for res in new_res:
            if res['year'] in years:
                res['score'] += 0.25


    results = sorted(new_res, key=lambda x: x['score'], reverse=True)
    return results[:n]


def retrieve_results_2(query, n=10):
    engine = get_engine()
    ids = engine.get_best_matches(query, n)
    db = get_db()
    sql_query = 'SELECT id, title, year FROM papers WHERE id IN (' + ','.join(
        (str(i) for i in ids)) + ')'
    results = db.execute(sql_query).fetchall()
    results = {r[0]: r[1:] for r in results}
    results = [results[i] for i in ids]
    return [{'title': res[0], 'year': res[1]} for res in results]


def retrieve_author_ids(query):
    authors = get_authors()
    db = get_db()
    return authors.retrieve(query, db)


# Retrieve info about the author, takes author_ids since one author can
# have 1+ entries
def retrieve_author_info(author_ids):
    authors = get_authors()
    db = get_db()
    results = {}
    results['papers'] = authors.get_relevant_papers(author_ids, db)
    results['coauthors'] = authors.get_coauthors(author_ids, db)
    results['years'] = authors.get_years(author_ids, db)
    results['keywords'] = authors.get_keywords(author_ids, db)
    results['topics'] = authors.get_topics(author_ids, db)
    results['similar_authors'] = authors.get_similar_authors(author_ids, db)
    results['similar_papers'] = authors.get_similar_papers(author_ids, db)
    results['citation_rating'] = authors.get_citation_rating(author_ids, db)
    return results


@app.route('/search')
def search():
    query = request.args.get('q', 'machine learning')

    qe = get_query_extractor()

    years = qe.extract_years(query)
    author_id_names = qe.extract_authors(query)
    author_names = [x[1] for x in author_id_names]

    db = get_db()
    authors = [Author(x[1], db) for x in author_id_names]
    authors = sorted(authors, key=lambda x: x.paper_count, reverse=True)[:5]

    search_results = retrieve_results_1(query, author_names=author_names, years=years)

    return render_template('search.html',
                           query=query,
                           search_results=search_results,
                           authors=authors)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/qbe', methods=['POST'])
def qbe():
    pdf_text = get_pdf_text_simple(request.files.getlist('file'))
    search_results = retrieve_results_2(pdf_text)
    return render_template('search.html',
                           query="QBE",
                           search_results=search_results)


@app.route('/authors')
def authors():
    query = request.args.get('q', 'Michael I. Jordan')

    try:
        author_ids = retrieve_author_ids(query)
    except NoAuthorsFoundException as e:
        return render_template('authors.html',
                               error=e.message,
                               query=query,
                               search_results=[])
    except MultipleAuthorsFoundException as e:
        return render_template('authors.html',
                               error=e.authors_names,
                               query=query,
                               search_results=[])
    else:
        search_results = retrieve_author_info(author_ids)
        papers = [{'year': paper[0], 'title': paper[1]} for paper in
                  search_results['papers']][:9]
        coauthors = [{'name': coauthor,
                      'count': search_results['coauthors'][coauthor]} for
                     coauthor in search_results['coauthors']][:10]
        papers_by_year = [{'year': year, 'count': search_results['years'][year]}
                          for year in search_results['years']]
        keywords = search_results['keywords'][:20]
        similar_authors = search_results['similar_authors']
        similar_papers = [{'title': title,
                           'year': search_results['similar_papers'][title]} for
                          title in search_results['similar_papers']][:9]
        rating = search_results['citation_rating']
        return render_template('authors.html',
                               error=None,
                               papers_by_year=papers_by_year,
                               query=query,
                               papers=papers,
                               rating=rating,
                               similar_papers=similar_papers,
                               coauthors=coauthors,
                               similar_authors=similar_authors,
                               keywords=keywords)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
