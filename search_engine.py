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
        stemmerLocal = stemmer.Stemmer()
    p = Parse(stemming=stemmerLocal, iIndexer=indexer)  # Changed by Lev


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

    i = 0 #first file index
    documents_list = [] #The list of tweets
    #Read all files:

    beforeStopPoints = np.linspace(500000, 10000000, 20)  # set the parts of the file, each number in this list is endpoint of 10% of the whole tweets
    stopPoints = []
    for point in beforeStopPoints:
        stopPoints.append(int(point))


    while i < 1:#len(listOfDoc): #Real is : while i < len(os.listdir(config.get__corpusPath())):
        startRead = time.time()
        documents_list = r.read_file(file_name=listOfDoc[i])
        i += 1
        endRead = time.time()
        readTime = endRead - startRead
        print("Read time: %s" % readTime)

        # Iterate over every document in the file
        for idx, document in enumerate(documents_list):

            if(number_of_documents == 300):
                break
            startParse = time.time()
            # parse the document
            parsed_document = p.parse_doc(document)
            number_of_documents += 1
            # index the document data
            pdl = len(parsed_document.term_doc_dictionary.keys())  # term_dict length
            if (pdl > 0):
                indexer.add_new_doc(parsed_document)
            endParse = time.time()
            print("elapsed time %s" % (endParse - startParse))
            print("Tw Num %s" % (number_of_documents))
            #if (number_of_documents in stopPoints):
            if (number_of_documents % 100 == 0):
                indexer.savePostingFile()

    print('Finished parsing and indexing. Starting to export files')
    if(number_of_documents not in stopPoints):
        indexer.savePostingFile()
    utils.save_obj(indexer.inverted_idx, "inverted_idx")
    utils.save_obj(indexer.term_max_freq, "term_max_freq")
    print ('Time to run: %s' % (startTimer - time.time()))




    #TODO: disable the option above and save posting files by 50,000 terms.


def load_index():
    print('Load inverted index')
    inverted_index = utils.load_obj("inverted_idx")
    return inverted_index

def load_max_freq():
    print('Load term max freq dictionary')
    inverted_index = utils.load_obj("term_max_freq")
    return inverted_index

def search_and_rank_query(query, inverted_index, term_max_freq, num_docs_to_retrieve, stemming=True):
    thisStemmer = None
    if(stemming == True):
        thisStemmer = stemmer.Stemmer()
    p = Parse(stemming=thisStemmer,invIdx=inverted_index)
    query_as_list = p.parse_sentence(query)
    searcher = Searcher(inverted_index,term_max_freq)
    relevant_docs = searcher.relevant_docs_from_posting(query_as_list)
    ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs)
    return searcher.ranker.retrieve_top_k(ranked_docs, num_docs_to_retrieve)


def main(corpus_path = "",output_path = "",stemming=True,queries = ["What to do"],num_docs_to_retrieve = 5):
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
        if(num_docs_to_retrieve > 2000):
            print("Number of docs to rertrieve cannot be more than 2000, so it changes to 2000 now")
            num_docs_to_retrieve=2000
        inverted_index = load_index()
        term_max_freq = load_max_freq()
        for query in queries_list:
            print('\n' + 'Query: ' + query)
            print('results:' + '\n')
            for doc_tuple in search_and_rank_query(query, inverted_index, term_max_freq, num_docs_to_retrieve, stemming):
                print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[1], doc_tuple[0]))
    except:
        print("Please enter queries first")
