# -*- coding: utf-8 -*-
import nltk
import re


class Preprocesser():
    """
    This class holds static methods for text preprocessing: such as abstract
    splitting. The following regexes are used in some of the functions.
    """
    # Add lines around chapter titles
    chapter_matcher = re.compile(r'(^[A-Z1-9][*\.A-Z \s]*)$',
                                 flags=re.MULTILINE)
    # Replace newlines between words with blanks.
    newline_matcher = re.compile(
        r'(?<=[&{}\;\"\'\w\(\)\.\,\?\-\/\\<>])\n(?=[&{}\;\"\'\w\(\)\.\,\?\-\/\\<>])')

    '''
    Match abstracts in two ways: either a paragraph before the introduction, 
    or the paragraph after "abstract"
    '''
    abstract_matcher = re.compile(
        r'([+{}=*&\[\]<>\;\:\"\'\w \(\)\.\,\?\-\/\\]*\s*\d+\s*introduction)|(a[bm][es]?[tl]rac[tf][\s-]*[+{}*=&\[\]\;\:<>\"\'\w \(\)\.\,\?\-\/\\]*)',
        flags=re.IGNORECASE)
    # Remove before and including "abstract"
    abstract_remover = re.compile(r'^.*(?i:a[bm][es]?[tl]rac[tf])',
                                  flags=re.IGNORECASE)
    whitespace_remover = re.compile(r'^[-:\s]*?(?=[A-Z])')

    stopwords = set(nltk.corpus.stopwords.words('english'))

    @classmethod
    def extract_abstract(cls, text):
        """
        :param text: Paper text to extract abstract from.
        :return: Abstract if possible, or empty string otherwise. Check the
        actual returned value: it might be more or less than the actual
        abstract.
        """
        try:
            text = re.sub(cls.chapter_matcher, r'\n\1\n', text)
            text = re.sub(cls.newline_matcher, r' ', text)
            text = re.search(cls.abstract_matcher, text).group(0)
            text = re.sub(cls.abstract_remover, r'', text)
            text = re.sub(cls.whitespace_remover, r'', text)
            return text[:text.rfind('.') + 1]
        except AttributeError:
            return ''

    @classmethod
    def tokenize(cls, text):
        return nltk.word_tokenize(text)

    @classmethod
    def filter_stopwords(cls, tokens):
        return filter(lambda token: token not in cls.stopwords and len(
            token) > 1 and token.isalnum() and not token.isdigit(), tokens)

    @classmethod
    def snowball_stemmer(cls, tokens):
        stemmer = nltk.stem.SnowballStemmer('english')
        return map(lambda token: stemmer.stem(token), tokens)

    @classmethod
    def porter_stemmer(cls, tokens):
        stemmer = nltk.stem.PorterStemmer()
        return map(lambda token: stemmer.stem(token), tokens)

    @classmethod
    def process(cls, text, stopwords=True, stemming='porter'):
        """
        :param text: Complete paper text.
        :param stopwords: If True, remove stopwords.
        :param stemming: Either 'porter' or 'snowball'. Can be None or empty
        string to remove stemming.
        :return: List of tokens.
        """
        tokens = cls.tokenize(text.lower())
        if stopwords:
            tokens = cls.filter_stopwords(tokens)
        if stemming is not None and stemming:
            stemming = stemming.lower()
            if stemming == 'porter':
                tokens = cls.porter_stemmer(tokens)
            elif stemming == 'snowball':
                tokens = cls.snowball_stemmer(tokens)
            else:
                raise Exception("Unsupported stemmer.")
        return tokens




class SnowballStemmer:
    '''
    Snowball stemmer from NLTK
    '''

    def stem(self, tokens):
        stemmer = nltk.stem.SnowballStemmer('english')
        return [stemmer.stem(t) for t in tokens]



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
