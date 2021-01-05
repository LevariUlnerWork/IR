import csv
import numpy as np
import operator
from local import LocalMethod
from reader import ReadFile
import stemmer
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import utils
import os
import time

def run_engine(corpus_path,output_path = "",stemming=False):
    """
    :return:
    """
    number_of_documents = 0
    stemmerLocal = None
    config = ConfigClass()
    savingPath = output_path + config.saveFilesWithoutStem + "/"
    indexer = Indexer(savingPath)
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
    beforeStopPoints = np.linspace(100000, 10000000, 100)  # set the parts of the files
    stopPoints = []
    for point in beforeStopPoints:
        stopPoints.append(int(point))


    while i < len(listOfDoc):
        documents_list = r.read_file(file_name=listOfDoc[i])
        i += 1

        # Iterate over every document in the file
        for idx, document in enumerate(documents_list):

            # if(number_of_documents == 300):
            #     break

            # parse the document
            parsed_document = p.parse_doc(document)
            number_of_documents += 1
            # index the document data
            pdl = len(parsed_document.term_doc_dictionary.keys())  # term_dict length
            if (pdl > 0):
                indexer.add_new_doc(parsed_document)
            if (number_of_documents in stopPoints):
                indexer.changeTweetTermsDict()


    indexer.closeIndexer(number_of_documents)



def load_index():
    inverted_index = utils.load_obj("inverted_idx")
    return inverted_index


def local_rank(query, inverted_index, posting, num_docs_to_retrieve, stemming, output_path):
    """
    This function gets a query and ranked the its relevant tweets. after that it takes the top 100 and checks if there
    are some words we can add to the query, for improving the ranks.
    in the end it returns the the top k tweets with their average rank for the 2 queries.
    :param query: query = array of terms
    :param num_docs_to_retrieve: k
    :param stemming: stemmer if it is exists
    :return: array of tuples  of top k relevant tweets for the query.
    """
    newLocal = LocalMethod(inverted_index,output_path, posting)
    thisStemmer=None
    if (stemming == True):
        thisStemmer = stemmer.Stemmer()
    p = Parse(stemming=thisStemmer, invIdx=inverted_index)
    query_as_list = p.parse_sentence(query)
    original_rank = search_and_rank_query(query_as_list, inverted_index, posting, num_docs_to_retrieve, stemming, output_path)
    rel_tweets = [] # docIDs to check

    for i in range (100):
        rel_tweets.append(original_rank[i][0])
    newQuery = []
    for term_query in query_as_list:
        newQuery.append(term_query)
        append_words = newLocal.new_words_to_query(term_query,rel_tweets)
        if(len(append_words) > 0):
            for word in append_words:
                if word not in newQuery and word not in query_as_list:
                    newQuery.append(word)

    if(len(newQuery) != len(query)):

        new_rank = search_and_rank_query(newQuery, inverted_index, posting, num_docs_to_retrieve, stemming, output_path)

        return  newLocal.compute_final_rank(original_rank,new_rank,num_docs_to_retrieve)
    else:
        return original_rank


def search_and_rank_query(query_as_list, inverted_index, posting_files , num_docs_to_retrieve, stemming=False, output_path=""):
    thisStemmer = None
    config = ConfigClass()
    loadingPath = output_path + config.saveFilesWithoutStem + "/"
    if(stemming == True):
        thisStemmer = stemmer.Stemmer()
        loadingPath = output_path + config.saveFilesWithStem + "/"

    # p = Parse(stemming=thisStemmer,invIdx=inverted_index)
    # query_as_list = p.parse_sentence(query)
    searcher = Searcher(inverted_index,loadingPath, posting_files)
    relevant_docs = searcher.relevant_docs_from_posting(query_as_list)
    ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs)
    return searcher.ranker.retrieve_top_k(ranked_docs, num_docs_to_retrieve)


def main(corpus_path = "Data2/",output_path = "posting",stemming=False,queries = ["What to do"],num_docs_to_retrieve = 2000):
    '''
    dict_final_data =  utils.load_inverted_index()
    final_data = {}
    for i in range (4):
        for term in dict_final_data[i].keys():
            final_data[term]  = [dict_final_data[i][term][0], dict_final_data[i][term][1]]
    sorted_final_data = sorted(final_data.items(), key=lambda item: item[1], reverse=False)
    n = len(sorted_final_data)
    ranks = range(1, n + 1)  # x-axis: the ranks
    freqs = [freq for (word, freq) in sorted_final_data]  # y-axis: the frequencies
    pylab.loglog(ranks, freqs, label='alice')  # this plots frequency, not relative frequency
    pylab.xlabel('log(rank)')
    pylab.ylabel('log(freq)')
    pylab.legend(loc='lower left')
    pylab.show()
    '''
    if("/" != corpus_path[len(corpus_path)-1]):
        corpus_path += "/"
    # if ("/" != output_path[len(output_path)-1]):
    #     output_path += "/"


    if(os.path.exists(output_path) == False):
        os.makedirs(output_path)
    #

    start_engine_time = time.time()

    run_engine(corpus_path,output_path,stemming)

    end_engine_time = time.time() - start_engine_time

    full_path = open('queries.txt',"r", encoding= 'utf8')
    queries_list = full_path.read().split("\n")

    #create csv file:
    with open("results.csv", 'w', newline='') as csvfile:
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
        if(num_docs_to_retrieve > 2000):
            num_docs_to_retrieve=2000
        inv_dict = load_index()
        inverted_index = inv_dict['inverted_idx']
        posting = inv_dict['posting']
        # term_max_freq = load_max_freq()
        start_query_time = time.time()
        for queryIndex in range(len(queries_list)):
            query = queries_list[queryIndex]
            if(query == ""): continue
            final_rank = local_rank(query, inverted_index, posting, num_docs_to_retrieve, stemming, output_path)
            for doc_tuple in final_rank:
                print(str(queryIndex) + ' tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[1], doc_tuple[0]))
                filewriter.writerow([queryIndex, "%s" % (doc_tuple[1]), doc_tuple[0]])
        end_query_time = time.time() - start_query_time

    timeFile = open("runtime.txt","w", encoding= 'utf8')
    timeFile.write("engine time: " + str(end_engine_time))
    timeFile.write("query time: " + str(end_query_time))




