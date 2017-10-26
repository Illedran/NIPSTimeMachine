import pickle
from sqlite3 import connect
import re
import nltk

chapter_matcher = re.compile(r'(^[A-Z1-9][*\.A-Z \s]*)$',
                             flags=re.MULTILINE)
newline_matcher = re.compile(
    r'(?<=[&{}\;\"\'\w\(\)\.\,\?\-\/\\<>])\n(?=[&{}\;\"\'\w\(\)\.\,\?\-\/\\<>])')
abstract_matcher = re.compile(
    r'(REFERENCES*[+{}*=&\[\]\;\:<>\"\'\w \(\)\.\,\?\-\/\\]*)|(References*[+{}*=&\[\]\;\:<>\"\'\w \(\)\.\,\?\-\/\\]*)',
    flags=re.IGNORECASE)
stopwords = set(nltk.corpus.stopwords.words('english'))

bindex = {}

# take this function and pass a paper to it to extract references
def referencer(paper):
    global bindex
    id = paper['id']
    text = paper['paper_text']
    try:
        text = re.sub(chapter_matcher, r'\n\1\n', text)
        text = re.sub(newline_matcher, r' ', text)
        text = re.search(abstract_matcher, text).group(0)
        tokens = [t for t in nltk.word_tokenize(text.lower())]
        stopped_tokens = [i for i in tokens if not i in stopwords]
        terms = filter(lambda x: len(x) > 2, stopped_tokens)
        terms = list(terms)
        for i in range(len(terms) - 1):
            biword = terms[i] + ' ' + terms[i + 1]
            if biword in bindex:
                bindex[biword].append(id)
            else:
                bindex[biword] = [id]
        return text
    except AttributeError:
        return ''
