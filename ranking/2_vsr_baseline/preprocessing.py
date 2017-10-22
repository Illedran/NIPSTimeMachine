import nltk


class BasicTokenizer:
    '''
    Uses NLTK word_toknizer, with conversion to lower case.
    '''

    def tokenize(self, text):
        return [t for t in nltk.word_tokenize(text.lower())]


class BasicFilter:
    '''
    Filters out stopwords from NLTK english stopword list
    '''

    def __init__(self):
        self.stopwords = set(nltk.corpus.stopwords.words('english'))

    def filt(self, tokens):
        def good(t):
            return (not t in self.stopwords
                    and len(t) > 1
                    and t.isalnum()
                    and not t.isdigit())
        return [t for t in tokens if good(t)]


class NoStemmer:
    '''
    Stemmer that does nothing
    '''

    def stem(self, tokens):
        return tokens


class SnowballStemmer:
    '''
    Snowball stemmer from NLTK
    '''

    def stem(self, tokens):
        stemmer = nltk.stem.SnowballStemmer('english')
        return [stemmer.stem(t) for t in tokens]


class Preprocessor:
    '''
    Adjustible text preprocessing pipeline
    '''

    def __init__(self):
        self.tokenizer = BasicTokenizer()
        self.filter = BasicFilter()
        self.stemmer = SnowballStemmer()

    def process(self, text):
        tokens = self.tokenizer.tokenize(text)
        tokens = self.filter.filt(tokens)
        tokens = self.stemmer.stem(tokens)
        return tokens

    def process_texts(self, texts=[]):
        return [self.process(text) for text in texts]
