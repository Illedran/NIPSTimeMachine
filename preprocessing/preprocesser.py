# -*- coding: utf-8 -*-
import re

class Preprocesser():
    '''
    This class holds static methods for text preprocessing: such as abstract
    splitting. The following regexes are used in some of the functions.
    '''
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

    @classmethod
    def extract_abstract(cls, text):
        '''
        :param text: Paper text to extract abstract from.
        :return: Abstract if possible, or empty string otherwise. Check the
        actual returned value: it might be more or less than the actual
        abstract.
        '''
        try:
            text = re.sub(cls.chapter_matcher, r'\n\1\n', text)
            text = re.sub(cls.newline_matcher, r' ', text)
            text = re.search(cls.abstract_matcher, text).group(0)
            text = re.sub(cls.abstract_remover, r'', text)
            text = re.sub(cls.whitespace_remover, r'', text)
            return text[:text.rfind('.') + 1]
        except AttributeError:
            return ''
