# -*- coding: utf-8 -*-
__author__ = "Andrea Nardelli"

import re
from abc import ABC, abstractmethod

import nltk


class Stemmer(ABC):
    """
    Generic stemming interface
    """

    @abstractmethod
    def stem(self, tokens):
        raise NotImplementedError()


class NoStemmer(Stemmer):
    """
    Stemmer that does nothing
    """

    def stem(self, tokens):
        return tokens


class SnowballStemmer(Stemmer):
    """
    Snowball stemmer from NLTK
    """

    def stem(self, tokens):
        stemmer = nltk.stem.SnowballStemmer('english')
        return map(stemmer.stem, tokens)


class PorterStemmer(Stemmer):
    """
    Porter stemmer from NLTK
    """

    def stem(self, tokens):
        stemmer = nltk.stem.PorterStemmer()
        return map(stemmer.stem, tokens)


class Tokenizer(ABC):
    @abstractmethod
    def tokenize(self, text):
        return NotImplementedError()


class NLTKTokenizer(Tokenizer):
    """
    Uses NLTK word tokenizer, with conversion to lower case.
    """

    def tokenize(self, text):
        return nltk.word_tokenize(text.lower())


class Filter(ABC):
    @abstractmethod
    def filter(self, tokens):
        return NotImplementedError()


class NLTKFilter(Filter):
    """
    Filters out stopwords from NLTK english stopword list
    """

    def __init__(self, language='english'):
        self.stopwords = set(nltk.corpus.stopwords.words(language))

    def filter(self, tokens):
        return filter(lambda token: token not in self.stopwords and len(
            token) > 1 and token.isalnum() and not token.isdigit(), tokens)


class Preprocessing(object):
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

    """
    Match abstracts in two ways: either a paragraph before the introduction, 
    or the paragraph after "abstract"
    """
    abstract_matcher = re.compile(
        r'([+{}=*&\[\]<>\;\:\"\'\w \(\)\.\,\?\-\/\\]*\s*\d+\s*introduction)|(a[bm][es]?[tl]rac[tf][\s-]*[+{}*=&\[\]\;\:<>\"\'\w \(\)\.\,\?\-\/\\]*)',
        flags=re.IGNORECASE)
    # Remove before and including "abstract"
    abstract_remover = re.compile(r'^.*a[bm][es]?[tl]rac[tf]',
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
        return NLTKTokenizer().tokenize(text)

    @classmethod
    def filter(cls, tokens):
        return NLTKFilter().filter(tokens)

    @classmethod
    def snowball_stemmer(cls, tokens):
        return SnowballStemmer().stem(tokens)

    @classmethod
    def porter_stemmer(cls, tokens):
        return PorterStemmer.stem(tokens)

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
            tokens = cls.filter(tokens)
        if stemming is not None and stemming:
            stemming = stemming.lower()
            if stemming == 'porter':
                tokens = cls.porter_stemmer(tokens)
            elif stemming == 'snowball':
                tokens = cls.snowball_stemmer(tokens)
            else:
                raise Exception("Unsupported stemmer.")
        return tokens

    @classmethod
    def process_bindex(cls, text):
        text = text.lower()
        tokens = cls.tokenize(text)
        tokens = cls.filter(tokens)

        return tokens


class Preprocessor(object):
    """
    Adjustible text preprocessing pipeline
    """

    def __init__(self):
        self.tokenizer = NLTKTokenizer()
        self.filter = NLTKFilter()
        self.stemmer = PorterStemmer()

    def process(self, text):
        tokens = self.tokenizer.tokenize(text)
        tokens = self.filter.filter(tokens)
        tokens = self.stemmer.stem(tokens)
        return tokens

    def process_texts(self, texts):
        return [self.process(text) for text in texts]
