import time
import numpy as np
from reader import ReadFile
import stemmer
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import utils
import os


def run_engine(corpus_path = "",output_path = "",stemming=True):
    """

    :return:
    """
    startTimer = time.time()
    number_of_documents = 0
    stemmerLocal = None
    config = ConfigClass()
    r = ReadFile(corpus_path=config.get__corpusPath())
    indexer = Indexer(config)
    if(stemming == True):
        stemmerLocal = stemmer.Stemmer(indexer)
    p = Parse(stemmerLocal, indexer)  # Changed by Lev


    #read all files from all folders:
    listOfFold = os.listdir(config.get__corpusPath()) #list of folders
    listOfDoc = [] #list of files and their paths
    for folder in listOfFold:
        if(".DS" in folder):
            continue
        listOfDocsBefore = os.listdir(config.get__corpusPath() + folder)
        for file in listOfDocsBefore:
            if (".DS" in file):
                continue
            listOfDoc += [folder + "/" + file]

    i = 2 #first file index
    documents_list = [] #The list of tweets
    #Read all files:
    startRead = time.time()
    while i < 3: #Real is : while i < len(os.listdir(config.get__corpusPath())):
        documents_list += r.read_file(file_name=listOfDoc[i])
        i += 1
    endRead = time.time()
    readTime = endRead - startRead
    print("elapsed time %s" % readTime)

    beforeStopPoints = np.linspace(int(len(documents_list)/10), len(documents_list),10)  # set the parts of the file, each number in this list is endpoint of 10% of the whole tweets
    stopPoints = []
    for point in beforeStopPoints:
        stopPoints.append(int(point))


    # Iterate over every document in the file
    for idx, document in enumerate(documents_list):

        startParse = time.time()
        # parse the document
        parsed_document = p.parse_doc(document)
        number_of_documents += 1
        # index the document data
        pdl = len(parsed_document.term_doc_dictionary.keys()) #term_dict length
        if(pdl > 0):
            indexer.add_new_doc(parsed_document)
        endParse = time.time()
        print("elapsed time %s" % (endParse - startParse))
        print ("Tw Num %s" % (number_of_documents))
        if(idx in stopPoints):
            indexer.savePostingFile()

    print('Finished parsing and indexing. Starting to export files')
    print ('Time to run: %s' % (startTimer - time.time()))

    utils.save_obj(indexer.inverted_idx, "inverted_idx")


    #TODO: disable the option above and save posting files by 50,000 terms.


def load_index():
    print('Load inverted index')
    inverted_index = utils.load_obj("inverted_idx")
    return inverted_index


def search_and_rank_query(query, inverted_index, k, stemming=True):
    p = Parse()
    query_as_list = p.parse_sentence(query)
    thisStemmer = None
    if(stemming == True):
        thisStemmer = stemmer.Stemmer(inv_dict=inverted_index)
    searcher = Searcher(inverted_index, thisStemmer)
    relevant_docs = searcher.relevant_docs_from_posting(query_as_list)
    ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs)
    return searcher.ranker.retrieve_top_k(ranked_docs, k)


def main(corpus_path = "",output_path = "",stemming=True,queries = ["1. What to do"],num_docs_to_retrieve = 0):
    run_engine(corpus_path = "",output_path = "",stemming=True)

    #query = input("Please enter a query: ")
    if(type(queries) == str):
        try: #If there is a file of queries
            r2 = ReadFile(queries)
            queries_list =r2.read_file(queries)
        except:#if queries is one line of query
            queries_list = [queries]

    else: #if queries is a list of queries
        queries_list = queries
    try:
        k = int(input("Please enter number of docs to retrieve: "))
        inverted_index = load_index()
        for query in queries_list:
            if(query[2] == " "):
                query = query[3:]
            else:
                query = query[2:]
            print('\n' + 'Query: ' + query)
            print('results:' + '\n')
            for doc_tuple in search_and_rank_query(query, inverted_index, k, stemming):
                print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[0], doc_tuple[1]))
    except:
        print("Please enter queries first")
