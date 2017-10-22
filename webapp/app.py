from flask import Flask, render_template, request, g
import pickle
from sqlite3 import connect
from engine import BasicEngine
app = Flask(__name__)

db_path = '../data/nips-papers/database.sqlite'

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

if __name__ == '__main__':
    app.run()