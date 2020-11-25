from nltk.stem import PorterStemmer

class Stemmer:
    def __init__(self,indexer):
        self.stemmer = PorterStemmer()
        self.indexer = indexer

    def stem_list(self, listStem):
        """
        This function stem a token
        :param token: string of a token
        :return: stemmed token
        """
        for word in listStem:
            wordInx = listStem.index(word)
            if len(word) > 1 and word[0].isupper() and ' ' not in word:# Change the words to Lower case or Upper Case, exclude Ishuts
                # for case: Max -> max
                if (word.lower() in self.indexer.inverted_idx.keys()):
                    word = word.lower()
                    listStem[wordInx] = self.stemmer.stem(word)
                # for case: Max -> MAX
                else:
                    word = word.upper()
                    listStem[wordInx] = word
        return listStem
