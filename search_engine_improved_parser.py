import csv
import pandas as pd
import numpy as np
from reader import ReadFile
import stemmer
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import utils
import os
import time



# DO NOT CHANGE THE CLASS NAME
class SearchEngine:

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation, but you must have a parser and an indexer.
    def __init__(self, config=None):
        self._config = config
        self._indexer = Indexer(config)
        self._parser = Parse(self._indexer)
        self._model = None

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def build_index_from_parquet(self, fn):
        """
        Reads parquet file and passes it to the parser, then indexer.
        Input:
            fn - path to parquet file
        Output:
            No output, just modifies the internal _indexer object.
        """

        output_path = ""
        stemmerLocal = None
        # if(stemming == True):
        #     stemmerLocal = stemmer.Stemmer()
        p = Parse(stemming=stemmerLocal, iIndexer=self._indexer)  # Changed by Lev



        df = pd.read_parquet(fn, engine="pyarrow")
        documents_list = df.values.tolist()
        number_of_documents = 0



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
                continue
            self._indexer.add_new_doc(parsed_document)
        print('Finished parsing and indexing.')

        self._indexer.save_index('inverted_idx')



    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        return self._indexer.load_index(fn)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_precomputed_model(self, model_dir=None):
        """
        Loads a pre-computed model (or models) so we can answer queries.
        This is where you would load models like word2vec, LSI, LDA, etc. and
        assign to self._model, which is passed on to the searcher at query time.
        """
        pass

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query):
        """
        Executes a query over an existing index and returns the number of
        relevant docs and an ordered list of search results.
        Input:
            query - string.
        Output:
            A tuple containing the number of relevant search results, and
            a list of tweet_ids where the first element is the most relavant
            and the last is the least relevant result.
        """
        searcher = Searcher(self._parser, self._indexer, model=self._model)
        return searcher.search(query)

    def main(self,corpus_path = "Data2/",output_path = "posting",stemming=False,queries = ["What to do"],num_docs_to_retrieve = 2000):
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

        self.build_index_from_parquet(corpus_path)

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
            start_query_time = time.time()
            for queryIndex in range(len(queries_list)):
                query = queries_list[queryIndex]
                if(query == ""): continue
                n_relevant, ranked_doc_ids=self.search(query)
                for doc_tuple_num in range(n_relevant):
                    print(f'tweet id: {ranked_doc_ids[doc_tuple_num]}, place_number: {doc_tuple_num}')
                    filewriter.writerow([queryIndex],[ "%s" % (ranked_doc_ids)])
            end_query_time = time.time() - start_query_time

        timeFile = open("runtime.txt","w", encoding= 'utf8')
        timeFile.write("engine time: " + str(end_engine_time))
        timeFile.write("query time: " + str(end_query_time))




