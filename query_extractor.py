import re
from tqdm import tqdm
from sqlite3 import connect
from collections import defaultdict


def _build_author_map(db):
    author_map = {}
    id_names = db.execute('select id, name from authors;').fetchall()
    for id_name in tqdm(id_names):
        author_name = id_name[1].lower()
        author_id = int(id_name[0])
        if not author_name in author_map:
            author_map[author_name] = author_id
    return author_map


def _build_author_term_map(author_map):
    term_regex = re.compile(r'\b([a-z]{2,})\b')
    term_map = defaultdict(set)
    names = author_map.keys()
    for name in tqdm(names):
        terms = term_regex.findall(name)
        for term in terms:
            # add author id to set corresponding to the name term
            term_map[term] |= {author_map[name]}
    return term_map


class Author:

    def __init__(self, name, db):
        self.name = name
        self.ids = db.execute('select id from authors where name like "%' + name + '%";').fetchall()
        count = db.execute('''select count(paper_id)
            from paper_authors join authors on author_id = authors.id
            where name like "%''' + name + '%";').fetchall()
        self.paper_count = int(count[0][0])

    def __repr__(self):
        return "{} {} {}\n".format(self.name, self.ids, self.paper_count)


class QueryExtractor:

    def __init__(self, db):
        self.author_map = _build_author_map(db)
        self.inv_author_map = {v: k for k, v in self.author_map.items()}
        self.term_author_map = _build_author_term_map(self.author_map)
        self.year_regex = re.compile(r'\b(\d{4})\b')
        self.author_term_regex = re.compile(r'\b([a-z]{2,})\b')

    def extract_years(self, query):
        return self.year_regex.findall(query)

    def extract_authors(self, query):
        query = query.lower()
        terms = self.author_term_regex.findall(query)
        possible_authors = set()
        for term in terms:
            possible_authors |= self.term_author_map[term]
        result = []
        for i in possible_authors:
            result.append((i, self.inv_author_map[i]))
        return result
