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

def retrieve_author_papers(author_ids):
    authors = get_authors()
    db = get_db()
    return authors.get_relevant_papers(author_ids, db)

def retrieve_coauthors(author_ids):
    authors = get_authors()
    db = get_db()
    return authors.get_coauthors(author_ids, db)

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
        search_results = retrieve_author_papers(author_ids)
        search_results = [{'title' : res[0], 'year' : res[1]} for res in search_results]
        coauthors = retrieve_coauthors(author_ids)
        # coauthors = coauthors.pop(query)
        coauthors = [{'name' : coauthor, 'count' : coauthors[coauthor]} for coauthor in coauthors]
        return render_template('authors.html',
        query=query,
        search_results=search_results,
        coauthors=coauthors)

if __name__ == '__main__':
    app.run()
