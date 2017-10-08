import nltk

#Uses NLTK word_toknizer, with alnum token filtration and conversion to lower case.
class BasicTokenizer:

	def tokenize(self, text):
		return [t for t in nltk.word_tokenize(text.lower()) if t.isalnum()]

#Filters out stopwords from NLTK english stopword list
class StopwordFilter:

	def __init__(self):
		self.stopwords = set(nltk.corpus.stopwords.words('english'))

	def filt(self, tokens):
		return [t for t in tokens if not t in self.stopwords]

#Stemmer that does nothing
class NoStemmer:

	def stem(self, tokens):
		return tokens

#Snowball stemmer from NLTK
class SnowballStemmer:

	def stem(self, tokens):
		stemmer = nltk.stem.SnowballStemmer('english')
		return [stemmer.stem(t) for t in tokens]

#Adjustible text preprocessing pipeline
class Preprocessor:

	def __init__(self):
		self.tokenizer = BasicTokenizer()
		self.filter = StopwordFilter()
		self.stemmer = SnowballStemmer()

	def process(self, text):
		tokens = self.tokenizer.tokenize(text)
		tokens = self.filter.filt(tokens)
		tokens = self.stemmer.stem(tokens)
		return tokens

	def process_texts(self, texts=[]):
		return [self.process(text) for text in texts]