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
        for wordInx in range(len(listStem)):
            word = listStem[wordInx]
            if word.upper() != word:
                listStem[wordInx] = self.stemmer.stem(word)
        return listStem


    def isfloat(value):
        if(value[0] == 'i' or value[0] == 'I'):
            return False
        try:
            float(value)
            return True
        except ValueError:
            return False