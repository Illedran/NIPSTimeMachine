from whoosh.index import create_in
from whoosh.fields import *
from whoosh.index import open_dir
from whoosh import index
from whoosh.qparser import QueryParser
import os.path
import csv

def create_schema():
	#construct a schema which specify what is indexed
	return Schema(id=ID, year=ID, title=TEXT, event_type=TEXT, pdf_name=TEXT(stored=True), abstract=TEXT, paper_text=TEXT)

def create_index(schema, index_name="index"):
	#create a index object if there isn't one yet
	if not os.path.exists(index_name):
		os.mkdir(index_name)
	# if not index.exists_in(index_name):
	# 	ix = create_in(index_name, schema)
	# 	return ix
	
	ix = create_in(index_name, schema)

	return ix

def load_csv_to_index(csv_file_name, index_name="index"):
	ix = open_dir(index_name)
	writer = ix.writer()
	# num = 100
	with open(csv_file_name) as csvfile:
		reader = csv.DictReader(csvfile)
		# for i in range(num):
			# item = reader.next()
			# print(item['id'],item['title'])
		for item in reader:
			writer.add_document(
				id = unicode(item['id']),
				year = unicode(item['year']),
				title = unicode(item['title']),
				event_type = unicode(item['event_type']),
				pdf_name = unicode(item['pdf_name']),
				abstract = unicode(item['abstract']),
				paper_text = unicode(item['paper_text']))

			# print item['paper_text']

		#after finishing adding documents to index, save the index
		writer.commit()	
	return ix

def search(query_str, search_field="title", index_name="index"):
	ix = open_dir(index_name)
	searcher = ix.searcher()
	myquery = QueryParser(search_field, ix.schema).parse(unicode(query_str))
	results = searcher.search(myquery)

	for x in results:
		print x

	return





def init():
	schema = create_schema()
	create_index(schema)
	load_csv_to_index('./nips-data/papers.csv')
	return
