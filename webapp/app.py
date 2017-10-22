from flask import Flask, render_template, request, g
import pickle
from sqlite3 import connect
from engine import BasicEngine
from authors import Authors
app = Flask(__name__)

db_path = '../nips-data/database.sqlite'

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

@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def retreive_results(query, n=10):
    engine = get_engine()
    ids = engine.get_best_matches(query, n)
    db = get_db()
    sql_query = 'select id, title, year from papers where id in (' + ','.join((str(i) for i in ids)) + ')'
    results = db.execute(sql_query).fetchall()
    results = {r[0] : r[1:] for r in results}
    return [results[i] for i in ids]

def retrieve_author_ids(query):
    authors = get_authors()
    db = get_db()
    return authors.retrieve(query, db)

# Retrieve info about the author, takes author_ids since one author can have 1+ entries
def retrieve_author_info(author_ids):
    authors = get_authors()
    db = get_db()
    results = {}
    results['papers'] = authors.get_relevant_papers(author_ids, db)
    results['coauthors'] = authors.get_coauthors(author_ids, db)
    results['years'] = authors.get_years(author_ids, db)
    results['keywords'] = authors.get_keywords(author_ids, db)
    results['topics'] = authors.get_topics(author_ids, db)
    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', 'machine learning')

    search_results = retreive_results(query)
    search_results = [{'title' : res[0], 'year' : res[1]} for res in search_results]
    return render_template('search.html',
        query=query,
        search_results=search_results)

@app.route('/authors')
def authors():
    query = request.args.get('q', 'Michael I. Jordan')

    author_ids = retrieve_author_ids(query)
    if type(author_ids) is str:
        return render_template('authors.html',
            error=author_ids,
            query=query,
            search_results=[])
    else:
        search_results = retrieve_author_info(author_ids)
        papers = [{'title' : paper[0], 'year' : paper[1]} for paper in search_results['papers']]
        coauthors = [{'name' : coauthor, 'count' : search_results['coauthors'][coauthor]} for coauthor in search_results['coauthors']][:10]
        papers_by_year = [{'year': year, 'count': search_results['years'][year]} for year in search_results['years']]
        keywords = search_results['keywords'][:10]
        return render_template('authors.html',
        papers_by_year=papers_by_year,
        query=query,
        papers=papers,
        coauthors=coauthors,
        keywords=keywords)

if __name__ == '__main__':
    app.run()
