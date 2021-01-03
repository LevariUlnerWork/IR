import math
import utils
import string
from operator import itemgetter
from queue import PriorityQueue
class Indexer:

    def __init__(self,savingPath = ""):


        self.inverted_idx = {}  # self.inverted_idx = [inverted_idx_nums, inverted_idx_ents, inverted_idx_others, inverted_idx_strs]
        self.alone_entities_dict = []
        self.tweetTerms = {}
        self.counterOfTweetTermsFiles = 0

        letters = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        for letter in string.ascii_lowercase:
            letters.append(letter)

        for letter in letters:
            utils.save_obj({}, savingPath + "posting_" + letter)
            for letter2 in letters:
                utils.save_obj({}, savingPath + "posting_" + letter + letter2)

        self.letters = letters
        utils.save_obj({}, savingPath + "postingOthers")
        self.savingPath = savingPath
        '''
        the posting files is built in this way:
        {term: [[freq of the term, docID, indexes of the term in this tweet, tf (would be in the end his cossim in this tweet)]]}
        
        '''

    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        docID = document.tweet_id
        document_dictionary = document.term_doc_dictionary # document_dictionary = {term:[[indexes],freq]
        self.tweetTerms [docID] = list(document_dictionary.keys())
        freq_max = sorted(list(document_dictionary.values()),key=itemgetter(1),reverse=True) [0][1] #Gets the maxFreq
        postingFile = {}
        postingFileName = ""
        # listOfUniques = [] #list of unique terms
        tfSquareSum = 0
        # self.term_max_freq[docID] = [0,{}]
        # Go over each term in the doc
        for term in sorted(list(document_dictionary.keys())):


                #Deciding the type of the term
                if (str(term[0]).lower() not in self.letters):  #others
                    type = 1
                elif(len(term) > 1):
                    if str(term[1]).lower() not in self.letters:
                        type = 1
                    else:  # strings
                        type = 2
                else:  #strings
                    type = 2

                if (' ' in term): #alone entities
                    if term in self.alone_entities_dict:
                        self.alone_entities_dict.remove(term)
                    else:
                        self.alone_entities_dict.append(term)

                if (type == 1):
                    if(postingFileName != "postingOthers"):
                        utils.save_obj(postingFile, self.savingPath + postingFileName)
                        postingFileName = "postingOthers"
                        postingFile = utils.load_obj(self.savingPath + postingFileName)

                elif(len(term)==1):
                    if postingFileName != "posting_" + term.lower():
                        utils.save_obj(postingFile, self.savingPath + postingFileName)
                        postingFileName = "posting_" + term.lower()
                        postingFile = utils.load_obj(self.savingPath + postingFileName)
                else:
                    if postingFileName !="posting_" + str(term[0]).lower() + str(term[1]).lower():
                        utils.save_obj(postingFile, self.savingPath + postingFileName)
                        postingFileName = "posting_" + term[0].lower() + term[1].lower()
                        postingFile = utils.load_obj(self.savingPath + postingFileName)
# this line

                indexes_t = document_dictionary[term][0]
                freq_t = document_dictionary[term][1]
                tf = freq_t / freq_max

                if term not in self.inverted_idx.keys():
                    postingFile[term] = []
                    postingFile[term].append([freq_t, docID, indexes_t,tf])
                    self.inverted_idx[term] = [1, freq_t, postingFileName]

                else:
                    #update inv_dict:
                    self.inverted_idx[term][0] += 1 # add another doc to the count in the inv_dict
                    self.inverted_idx[term][1] += freq_t
                    postingFile[term].append([freq_t, docID, indexes_t,tf])

        utils.save_obj(postingFile, self.savingPath + postingFileName)



    def changeTweetTermsDict(self):
        utils.save_obj(self.tweetTerms, self.savingPath + "TweetTerm_%s" % (self.counterOfTweetTermsFiles))
        self.counterOfTweetTermsFiles += 1
        self.tweetTerms = {}

    def closeIndexer(self, numberOfTweets):
        utils.save_obj(self.tweetTerms, self.savingPath + "TweetTerm_%s" % (self.counterOfTweetTermsFiles))
        self.computeTfIdf(numberOfTweets)
        self.deleteSingleEntities()
        utils.save_obj(self.inverted_idx, "inverted_idx")

    def computeTfIdf(self, numberOfTweets):
        counterTweetsFiles = self.counterOfTweetTermsFiles
        postingFile = {}
        postingFileName = ""
        while counterTweetsFiles >= 0:
            tweetsFile = utils.load_obj(self.savingPath + "TweetTerm_%s" % (counterTweetsFiles))
            for tweet in tweetsFile.keys():
                docSensorPerTerm = {}
                tfIdfThisTweet = {}
                for term in sorted(tweetsFile[tweet]):


                    #First - get the posting file
                    if (str(term[0]).lower() not in self.letters):  # others
                        type = 1
                    elif (len(term) > 1):
                        if str(term[1]).lower() not in self.letters:
                            type = 1
                        else:  # strings
                            type = 2
                    else:  # strings
                        type = 2

                    sopposedPostingName = ""

                    if(type == 1):
                        sopposedPostingName = "postingOthers"
                    elif len(term) == 1:
                            sopposedPostingName = "posting_" + term.lower()
                    else:
                        sopposedPostingName = "posting_" + str(term[0]).lower() + str(term[1]).lower()

                    if(postingFileName != sopposedPostingName):
                        utils.save_obj(postingFile, self.savingPath + postingFileName)
                        postingFileName = sopposedPostingName
                        postingFile = utils.load_obj(self.savingPath + postingFileName)

                    tf = 1

                    for docData in range (len(postingFile[term])):
                        if postingFile[term][docData][1] == tweet:
                            tf = postingFile[term][docData][3]
                            docSensorPerTerm[term] = docData
                            break
                    idf_Term = math.log2(numberOfTweets / self.inverted_idx[term][0])
                    tfIdfThisTweet[term] = tf*idf_Term

                tfIdfThisTweetPowList = [math.pow(x,2) for x in tfIdfThisTweet.values()]
                denominator = math.sqrt(sum(tfIdfThisTweetPowList))

                for term in sorted(tweetsFile[tweet]):
                    #First - get the posting file
                    if (str(term[0]).lower() not in self.letters):  # others
                        type = 1
                    elif (len(term) > 1):
                        if str(term[1]).lower() not in self.letters:
                            type = 1
                        else:  # strings
                            type = 2
                    else:  # strings
                        type = 2

                    sopposedPostingName = ""

                    if (type == 1):
                        sopposedPostingName = "postingOthers"
                    elif len(term) == 1:
                        sopposedPostingName = "posting_" + term.lower()
                    else:
                        sopposedPostingName = "posting_" + str(term[0]).lower() + str(term[1]).lower()

                    if (postingFileName != sopposedPostingName):
                        utils.save_obj(postingFile, self.savingPath + postingFileName)
                        postingFileName = sopposedPostingName
                        postingFile = utils.load_obj(self.savingPath + postingFileName)

                    postingFile[term][docSensorPerTerm[term]][3] = tfIdfThisTweet[term] / denominator #Cossim of the term in this tweet
            counterTweetsFiles -= 1
        utils.save_obj(postingFile, self.savingPath + postingFileName)


    def deleteSingleEntities(self):
        for term in self.alone_entities_dict:
            self.inverted_idx.pop(term)
        self.alone_entities_dict = {}



    def isfloat(self, value):
        if(value[0] == 'i' or value[0] == 'I'):
            return False
        try:
            float(value)
            return True
        except ValueError:
            return False

