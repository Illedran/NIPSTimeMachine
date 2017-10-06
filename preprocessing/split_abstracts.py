# -*- coding: utf-8 -*-
import re
import pandas as pd

data = pd.read_csv('nips-data/papers.csv')

# Data cleaners
# Add lines around chapter titles
chapter_matcher = re.compile(r'(^[A-Z1-9][*\.A-Z \s]*)$', flags=re.MULTILINE)
# Replace newlines between words with blanks.
newline_matcher = re.compile(r'(?<=[&{}\;\"\'\w\(\)\.\,\?\-\/\\<>])\n(?=[&{}\;\"\'\w\(\)\.\,\?\-\/\\<>])')
# Match abstracts in two ways: either a paragraph before the introduction, or the paragraph after "abstract"
abstract_matcher = re.compile(
    r'([+{}=*&\[\]<>\;\:\"\'\w \(\)\.\,\?\-\/\\]*\s*\d+\s*introduction)|(a[bm][es]?[tl]rac[tf][\s-]*[+{}*=&\[\]\;\:<>\"\'\w \(\)\.\,\?\-\/\\]*)',
    flags=re.IGNORECASE)
# Remove before and including "abstract"
abstract_remover = re.compile(r'^.*(?i:a[bm][es]?[tl]rac[tf])[-:\s]*?(?=[A-Z])')


def cleaner(text):
    try:
        text = re.sub(chapter_matcher, r'\n\1\n', text)
        text = re.sub(newline_matcher, r' ', text)
        text = re.search(abstract_matcher, text).group(0)
        text = re.sub(abstract_remover, r'', text)
        return text[:text.rfind('.') + 1]
    except AttributeError:
        return ''

data.abstract = data.paper_text.apply(cleaner)
