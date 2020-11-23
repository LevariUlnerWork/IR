from nltk.stem import PorterStemmer

class Stemmer:
    def __init__(self):
        self.stemmer = PorterStemmer()

    def stem_list(self, listStem):
        """
        This function stem a token
        :param token: string of a token
        :return: stemmed token
        """
        for word in listStem:
            wordInx = listStem.index(word)
            listStem[wordInx] =  self.stemmer.stem(word)
        return listStem
