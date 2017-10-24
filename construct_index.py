from whoosh.index import create_in
from whoosh.fields import *
from whoosh.index import open_dir
from whoosh import index
from whoosh.qparser import QueryParser
from whoosh.scoring import TF_IDF
from whoosh.scoring import Frequency
import os.path
import csv

def create_schema():
	#construct a schema which specify what is indexed
	return Schema(id=ID(stored=True), year=ID(stored=True), title=TEXT(stored=True), event_type=TEXT, pdf_name=TEXT, abstract=TEXT, paper_text=TEXT(stored=True))

def create_index(schema, index_name="index_with_content"):
	#create a index object if there isn't one yet
	if not os.path.exists(index_name):
		os.mkdir(index_name)
	# if not index.exists_in(index_name):
	# 	ix = create_in(index_name, schema)
	# 	return ix
	
	ix = create_in(index_name, schema)

	return ix

def load_csv_to_index(csv_file_name, index_name="index_with_content"):
	ix = open_dir(index_name)
	writer = ix.writer()
	num = 100
	with open(csv_file_name) as csvfile:
		reader = csv.DictReader(csvfile)
		# for i in range(num):
			# item = reader.next()
			# print(item['id'],item['title'])
		for item in reader:
			writer.add_document(
				id = item['id'],
				year = item['year'],
				title = item['title'],
				event_type = item['event_type'],
				pdf_name = item['pdf_name'],
				abstract = item['abstract'],
				paper_text = item['paper_text'])

			# print item['paper_text']

		#after finishing adding documents to index, save the index
		writer.commit()	
	return ix

def search(query_str, search_field="paper_text", index_name="index_with_content"):
	ix = open_dir(index_name)
	searcher = ix.searcher()	#BM25F
	# searcher = ix.searcher(weighting = TF_IDF)	#TF_IDF
	# searcher = ix.searcher(weighting = Frequency) #Frequency
	myquery = QueryParser(search_field, ix.schema).parse(query_str)
	results = searcher.search(myquery, limit=100)

	# for x in results:
	# 	print(x)

	return results





def init():
	schema = create_schema()
	create_index(schema, index_name="index_with_content")
	load_csv_to_index('papers.csv', index_name="index_with_content")
	return

if __name__ == '__main__':
	init()