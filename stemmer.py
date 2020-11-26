from nltk.stem import PorterStemmer

class Stemmer:
    def __init__(self,indexer=None, inv_dict = None):
        self.stemmer = PorterStemmer()
        if(indexer == None):
            self.inv_dict = inv_dict
        else:
            self.inv_dict = indexer.inverted_idx

    def stem_list(self, listStem):
        """
        This function stem a token
        :param token: string of a token
        :return: stemmed token
        """
        for word in listStem:
            type = [0, 1, 2, 3]
            if (Stemmer.isfloat(word) == True):
                type = 0
            elif (len(word) == 1):
                type = 1
            elif ('_' in word):
                type = 2
            else:
                type = 3
            wordInx = listStem.index(word)
            if len(word) > 1 and word[0].isupper() and ' ' not in word:# Change the words to Lower case or Upper Case, exclude Ishuts
                # for case: Max -> max
                if (word.lower() in self.inv_dict[type].keys()):
                    word = word.lower()
                    listStem[wordInx] = self.stemmer.stem(word)
                # for case: Max -> MAX
                else:
                    word = word.upper()
                    listStem[wordInx] = word
        return listStem


    def isfloat(value):
        if(value[0] == 'i' or value[0] == 'I'):
            return False
        try:
            float(value)
            return True
        except ValueError:
            return False