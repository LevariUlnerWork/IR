import csv
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


def run_engine(corpus_path,output_path = "",stemming=True):
    """

    :return:
    """
    startTimer = time.time()
    number_of_documents = 0
    stemmerLocal = None
    config = ConfigClass()
    indexer = Indexer()
    savingPath = output_path + config.saveFilesWithoutStem + "/"
    if(stemming == True):
        stemmerLocal = stemmer.Stemmer()
        savingPath = output_path + config.saveFilesWithStem + "/"
    p = Parse(stemming=stemmerLocal, iIndexer=indexer)  # Changed by Lev
    if os.path.exists(savingPath) == False:
        os.makedirs(savingPath)
    r = ReadFile(corpus_path)

    #read all files from all folders:
    listOfFold = os.listdir(corpus_path) #list of folders
    listOfDoc = [] #list of files and their paths
    for folder in listOfFold:
        if(".DS" in folder):
            continue
        if(".parquet" in folder):
            listOfDoc += [folder]
            continue
        listOfDocsBefore = os.listdir(corpus_path + folder)
        for file in listOfDocsBefore:
            if (".DS" in file):
                continue
            listOfDoc += [folder + "/" + file]

    i = 0    #first file index
    documents_list = [] #The list of tweets
    #Read all files:

    beforeStopPoints = np.linspace(500000, 10000000, 20)  # set the parts of the file, each number in this list is endpoint of 10% of the whole tweets
    stopPoints = []
    for point in beforeStopPoints:
        stopPoints.append(int(point))


    while i < len(listOfDoc):
        startRead = time.time()
        documents_list = r.read_file(file_name=listOfDoc[i])
        i += 1
        endRead = time.time()
        readTime = endRead - startRead
        print("Read time: %s" % readTime)

        # Iterate over every document in the file
        for idx, document in enumerate(documents_list):

            # if(number_of_documents == 350):
            #     break
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
            if (number_of_documents in stopPoints):
            # if (number_of_documents % 100 == 0):
                indexer.savePostingFile(savingPath)

    print('Finished parsing and indexing. Starting to export files')
    if(number_of_documents not in stopPoints):
        indexer.savePostingFile(savingPath)

    # Delete little entities:
    for entity in list(indexer.inverted_idx.keys()):
        if (indexer.inverted_idx[entity][0] == 1):
            # posting = indexer.inverted_idx[2][entity][2][0]
            # posting_dict = utils.load_obj(savingPath + posting)
            # posting_dict.pop(entity)
            # utils.save_obj(posting_dict, savingPath + posting)
            indexer.inverted_idx.pop(entity)

    utils.save_obj(indexer.inverted_idx, "inverted_idx")
    utils.save_obj(indexer.term_max_freq, "term_max_freq")
    print ('Time to run: %s' % (startTimer - time.time()))






def load_index():
    print('Load inverted index')
    inverted_index = utils.load_obj("inverted_idx")
    return inverted_index

def load_max_freq():
    print('Load term max freq dictionary')
    inverted_index = utils.load_obj("term_max_freq")
    return inverted_index

def search_and_rank_query(query, inverted_index, term_max_freq, num_docs_to_retrieve, stemming=True, output_path=""):
    thisStemmer = None
    config = ConfigClass()
    loadingPath = output_path + config.saveFilesWithoutStem + "/"
    if(stemming == True):
        thisStemmer = stemmer.Stemmer()
        loadingPath = output_path + config.saveFilesWithStem + "/"

    p = Parse(stemming=thisStemmer,invIdx=inverted_index)
    query_as_list = p.parse_sentence(query)
    searcher = Searcher(inverted_index,term_max_freq,loadingPath)
    relevant_docs = searcher.relevant_docs_from_posting(query_as_list)
    ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs)
    return searcher.ranker.retrieve_top_k(ranked_docs, num_docs_to_retrieve)


def main(corpus_path = "Data/",output_path = "posting",stemming=True,queries = ["What to do"],num_docs_to_retrieve = 2000):

    if("/" != corpus_path[len(corpus_path)-1]):
        corpus_path += "/"
    if ("/" != output_path[len(output_path)-1]):
        output_path += "/"

    if(os.path.exists(output_path) == False):
        os.makedirs(output_path)

    run_engine(corpus_path,output_path,stemming)

    full_path = open('queries.txt',"r", encoding= 'utf8')
    queries_list = full_path.read().split("\n")

    #create csv file:
    with open("results.csv", 'w', newline='') as csvfile:
        startCode = time.time()
        filewriter = csv.writer(csvfile)
        filewriter.writerow(["Query_num", "Tweet_id", "Rank"])

        #query = input("Please enter a query: ")
        if(type(queries) == str):
            try: #If there is a file of queries
                full_path = open(queries, "r",encoding='utf8')
                queries_list += full_path.read(queries).split('\n')
            except:#if queries is one line of query
                queries_list += [queries]

        else: #if queries is a list of queries
            queries_list += queries
        try:
            if(num_docs_to_retrieve > 2000):
                print("Number of docs to rertrieve cannot be more than 2000, so it changes to 2000 now")
                num_docs_to_retrieve=2000
            inverted_index = load_index()
            term_max_freq = load_max_freq()
            for queryIndex in range(len(queries_list)):
                query = queries_list[queryIndex]
                print('\n' + 'Query: ' + query)
                print('results:' + '\n')
                for doc_tuple in search_and_rank_query(query, inverted_index, term_max_freq, num_docs_to_retrieve, stemming ,output_path):
                    print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[1], doc_tuple[0]))
                    filewriter.writerow([queryIndex, "%s" % (doc_tuple[1]), doc_tuple[0]])
        except:
            pass
    todebug = True
