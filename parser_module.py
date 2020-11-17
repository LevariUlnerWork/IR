
import re
from nltk.stem import PorterStemmer
from document import Document


class Parse:

    def __init__(self):
        #self.stop_words = stopwords.words('english') - we are not use this stop words
        full_path = open('stop-words.txt',"r")
        listOfStopWords = full_path.read()
        #print(listOfStopWords)
        full_path.close()
        self.stop_words = listOfStopWords.split(" ")
        #print(type(self.stop_words))
        '''
        #shortcutdictionary
        self.shortcutDict = {}
        with open('shortcut.txt') as f:
            for line in f:
                line = line.rstrip('\n')
                (key, val) = line.split(':')
                self.shortcutDict[key] = val
        '''


    shortcutDict = {}
    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text: Every tweet/query
        :return: list of terms
        """
        #Not using - text_tokens = word_tokenize(text)
        text_tokens = Parse.tokenize_words(text)

        #if the len of query without stop-words is 0 - dont use stop-words -----------------CHECK------------------------
        #if(len(w.lower() for w in query if w not in self.stop_words) == 0):
        #    text_tokens_without_stopwords = [w.lower() for w in text_tokens]
        #else:
        text_tokens_without_stopwords = [w.lower() for w in text_tokens if w not in self.stop_words]

        return text_tokens_without_stopwords

    #this function is used for the tweets
    def parse_doc(self, doc_as_list):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-preseting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        retweet_text = doc_as_list[4]
        retweet_url = doc_as_list[5]
        quote_text = doc_as_list[6]
        quote_url = doc_as_list[7]
        term_dict = {}
        tokenized_text = self.parse_sentence(full_text)

        doc_length = len(tokenized_text)  # after text operations.

        for term in tokenized_text:
            if term not in term_dict.keys():
                term_dict[term] = 1
            else:
                term_dict[term] += 1

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length)
        return document

    #stemming - save the suffix
    def stemming(text):
        suffixWord = PorterStemmer()
        listOfSuffix = text.split(' ')
        for word in text:
            listOfSuffix.append(suffixWord.stem(word))
            listOfSuffix.remove(word)


    #Punctuation
    def punctuation(text):
        # if (('?' or '(' or ')' or '[' or ']' or '{' or '}' or "\n" or "\t" or "\'" or imojis or ':' or ';' or '!' or "'") in text):
        text = text.replace('?', ' ')
        text = text.replace('!', ' ')
        text = text.replace('&', ' ')
        text = text.replace(';', ' ')
        text = text.replace(':', ' ')
        #text = text.replace("'", ' ')
        text = text.replace('(', ' ')
        text = text.replace(')', ' ')
        text = text.replace('[', ' ')
        text = text.replace(']', ' ')
        text = text.replace('{', ' ')
        text = text.replace('}', ' ')
        text = text.replace('\n', ' ')
        text = text.replace('\t', ' ')
        #text = text.replace("\'", ' ')
        text = text.encode("ascii", "ignore").decode()  # delete all illegal characters like emojis

        listWithoutPunc = text.split(' ')

        #Handle urls:
        domain=[]#domain=""
        # for case:www.abc.com -> URL
        if 'https://' in text:
            for word in listWithoutPunc:
                if ('https://' in word):
                    domain = word.split('//')  # domain = [{"https:", "t.co/sdfs..."]
                    domain = domain[1].split('/')  # domai = ["t.co", "sdfs"...]
                    domain = domain[0]  # domain = "t.co"


        #this list is not final
        #punctuationList = [' ','&',';','(',')','[',']','{','}','?','!', '"' , ':'] #ignore them=

        for word in listWithoutPunc:
            numIndex = listWithoutPunc.index(word)

            #check shortcuts
            shortcutDict = {"ain't": "am not / are not","aren't": "are not / am not","can't": "cannot","can't've": "cannot have",
                             "'cause": "because","could've": "could have","couldn't": "could not","couldn't've": "could not have",
                             "didn't": "did not","doesn't": "does not","don't": "do not","hadn't": "had not","hadn't've": "had not have",
                             "hasn't": "has not","haven't": "have not","he'd": "he had / he would","he'd've": "he would have",
                             "he'll": "he shall / he will","he'll've": "he shall have / he will have","he's": "he has / he is",
                             "how'd": "how did","how'd'y": "how do you","how'll": "how will","how's": "how has / how is",
                             "i'd": "I had / I would","i'd've": "I would have","i'll": "I shall / I will","i'll've": "I shall have / I will have",
                             "i'm": "I am","i've": "I have","isn't": "is not","it'd": "it had / it would","it'd've": "it would have",
                             "it'll": "it shall / it will","it'll've": "it shall have / it will have","it's": "it has / it is","let's": "let us",
                             "ma'am": "madam","mayn't": "may not","might've": "might have","mightn't": "might not","mightn't've": "might not have",
                             "must've": "must have","mustn't": "must not","mustn't've": "must not have","needn't": "need not","needn't've": "need not have",
                             "o'clock": "of the clock","oughtn't": "ought not","oughtn't've": "ought not have","shan't": "shall not","sha'n't": "shall not",
                             "shan't've": "shall not have","she'd": "she had / she would","she'd've": "she would have","she'll": "she shall / she will",
                             "she'll've": "she shall have / she will have","she's": "she has / she is","should've": "should have","shouldn't": "should not",
                             "shouldn't've": "should not have","so've": "so have","so's": "so as / so is","that'd": "that would / that had",
                             "that'd've": "that would have","that's": "that has / that is","there'd": "there had / there would",
                             "there'd've": "there would have","there's": "there has / there is","they'd": "they had / they would",
                             "they'd've": "they would have","they'll": "they shall / they will","they'll've": "they shall have / they will have",
                             "they're": "they are","they've": "they have","to've": "to have","wasn't": "was not","we'd": "we had / we would",
                             "we'd've": "we would have","we'll": "we will","we'll've": "we will have","we're": "we are","we've": "we have",
                             "weren't": "were not","what'll": "what shall / what will","what'll've": "what shall have / what will have",
                             "what're": "what are","what's": "what has / what is","what've": "what have","when's": "when has / when is",
                             "when've": "when have","where'd": "where did","where's": "where has / where is","where've": "where have",
                             "who'll": "who shall / who will","who'll've": "who shall have / who will have","who's": "who has / who is",
                             "who've": "who have","why's": "why has / why is","why've": "why have","will've": "will have","won't": "will not",
                             "won't've": "will not have","would've": "would have","wouldn't": "would not","wouldn't've": "would not have",
                             "y'all": "you all","y'all'd": "you all would","y'all'd've": "you all would have","y'all're": "you all are",
                             "y'all've": "you all have","you'd": "you had / you would","you'd've": "you would have","you'll": "you shall / you will",
                             "you'll've": "you shall have / you will have","you're": "you are","you've": "you have"}

            if word in shortcutDict.keys():
                i=numIndex
                listWithoutPunc.pop(numIndex)
                word = shortcutDict[word]
                for term in word.split(' '):
                    listWithoutPunc.insert(i, term)
                    i+=1
                numIndex = i
            #continue

            shortscriptDict = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸","9": "⁹",
                               "a": "ᵃ", "b": "ᵇ", "c": "ᶜ", "d": "ᵈ", "e": "ᵉ", "f": "ᶠ", "g": "ᵍ", "h": "ʰ", "i": "ᶦ","j": "ʲ",
                               "k": "ᵏ", "l": "ˡ", "m": "ᵐ", "n": "ⁿ", "o": "ᵒ", "p": "ᵖ", "q": "۹", "r": "ʳ", "s": "ˢ","t": "ᵗ",
                               "u": "ᵘ", "v": "ᵛ", "w": "ʷ", "x": "ˣ", "y": "ʸ", "z": "ᶻ", "A": "ᴬ", "B": "ᴮ", "C": "ᶜ","D": "ᴰ",
                               "E": "ᴱ", "F": "ᶠ", "G": "ᴳ", "H": "ᴴ", "I": "ᴵ", "J": "ᴶ", "K": "ᴷ", "L": "ᴸ", "M": "ᴹ","N": "ᴺ",
                               "O": "ᴼ", "P": "ᴾ", "Q": "Q", "R": "ᴿ", "S": "ˢ", "T": "ᵀ", "U": "ᵁ", "V": "ⱽ", "W": "ᵂ","X": "ˣ",
                               "Y": "ʸ", "Z": "ᶻ", "+": "⁺", "-": "⁻", "=": "⁼", "(": "⁽", ")": "⁾"}

            if word in shortscriptDict.keys():
                i=numIndex
                word = shortscriptDict[word]
                listWithoutPunc.insert(numIndex, word)


            if("https" not in word):
                if(('.' or ',' or '/' or '-') in word and len(word) > 1):
                    for i in [',','.','/','-']:
                        seperateWordList = word.split(i)
                        isNumber = True
                        for inWord in seperateWordList:
                            if not inWord.isdigit():
                                isNumber = False
                        # for case: 13,333
                        if (isNumber and i == ','):
                            if (',' in word):
                                listWithoutPunc[numIndex] = word.replace(',', '')
                            else: # 123.33 | 213/2312
                                continue
                        # for case: go. | go,
                        elif (len(seperateWordList) >= 2):
                            if(len(seperateWordList[1]) == 0):
                                if (',' in word and i == ','):
                                    word = word.replace(',', '')
                                if ('.' in word and i == '.'):
                                    word = word.replace('.', '')
                                if ('/' in word and i == '/'):
                                    word = word.replace('/', '')
                                if ('-' in word and i == '-'):
                                    word = word.replace('-', '')
                                listWithoutPunc[numIndex] = word
                            else:
                                # for case: "His/Her | his,her"
                                listWithoutPunc.pop(numIndex)
                                listWithoutPunc += seperateWordList
                        else:
                            if (',' in word and i == ','):
                                word = word.replace(',', '')
                                listWithoutPunc[numIndex] = word
                            if ('.' in word and i == '.'):
                                word = word.replace('.', '')
                                listWithoutPunc[numIndex] = word
                            if ('/' in word and i == '/'):
                                word = word.replace('/', '')
                                listWithoutPunc[numIndex] = word
                            if ('-' in word and i == '-'):
                                word = word.replace('-', '')
                                listWithoutPunc[numIndex] = word
                            else:
                                continue
                if(word == ''): # Delete non words
                    listWithoutPunc.remove('')
            else: # Delete urls
                listWithoutPunc.remove(word)

        if(len(domain)>0):
            return listWithoutPunc+[domain]
        else:
            return listWithoutPunc

    def isfloat(value):
        try:
            float(value)
            return True
        except ValueError:
            return False


    def tokenize_words(text):
        listOfTokens = Parse.punctuation(text)

        #-----------------------------------------CHECK-------------------------------------------------
        shortscriptDict = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶","7": "⁷", "8": "⁸", "9": "⁹",
                           "a": "ᵃ", "b": "ᵇ", "c": "ᶜ", "d": "ᵈ","e": "ᵉ", "f": "ᶠ", "g": "ᵍ", "h": "ʰ", "i": "ᶦ", "j": "ʲ",
                           "k": "ᵏ","l": "ˡ", "m": "ᵐ", "n": "ⁿ", "o": "ᵒ", "p": "ᵖ", "q": "۹", "r": "ʳ","s": "ˢ", "t": "ᵗ",
                           "u": "ᵘ", "v": "ᵛ", "w": "ʷ", "x": "ˣ", "y": "ʸ","z": "ᶻ", "A": "ᴬ", "B": "ᴮ", "C": "ᶜ", "D": "ᴰ",
                           "E": "ᴱ", "F": "ᶠ","G": "ᴳ", "H": "ᴴ", "I": "ᴵ", "J": "ᴶ", "K": "ᴷ", "L": "ᴸ", "M": "ᴹ","N": "ᴺ",
                           "O": "ᴼ", "P": "ᴾ", "Q": "Q", "R": "ᴿ", "S": "ˢ", "T": "ᵀ","U": "ᵁ", "V": "ⱽ", "W": "ᵂ", "X": "ˣ",
                           "Y": "ʸ", "Z": "ᶻ", "+": "⁺","-": "⁻", "=": "⁼", "(": "⁽", ")": "⁾"}



        #with open('subscript.txt') as file:
            #for line in file:
                #(key, val) = line.split(':')
              #  shortscriptDict[key] = val
     #   print(shortscriptDict)

        #textExam2 = "9 ₀₁₂₃₄₅₆₇₈₉"
        #for sub in textExam2.split():
            #if sub in shortscriptDict.keys():
                #textExam2 = textExam2.replace(sub, shortscriptDict[sub])
        #print(textExam2)
        #----------------------------------------until here-----------------------------------------------


        for wordToken in listOfTokens:

            wordIndex= listOfTokens.index(wordToken)

            if(len(wordToken) > 0):
                #tags
                if(wordToken[0] == '@' and len(wordToken)!=1):
                    listOfTokens.insert(wordIndex ,"@")
                    wordIndex+=1
                    listOfTokens.insert(wordIndex, wordToken[1:])

                #dollar
                if('$' in wordToken):
                    listOfTokens.insert(wordIndex+1, "dollar")
                    if(len(wordToken.replace('$','')) != 0 ): # for case: 2000$
                        listOfTokens[listOfTokens.index(wordToken)] = wordToken.replace('$','')
                        wordToken = wordToken.replace('$', '')
                    else: # for case: $$
                        listOfTokens.remove(wordToken)
                        continue

                #Hashtags
                if (wordToken[0] == '#' and not wordToken[1:].isdigit()):
                    iIndex = wordIndex + 1
                    finalWord = "#"  # Final Word: "#stayathome"
                    if(wordToken.find("_") != -1):# if there is a '_'
                        wordToken = wordToken[1:] #now: "stay_at_home"
                        #For case: "#Stay_At_Home" and "#stay_at_home"
                        for partOfToken in wordToken.split('_'):#For case: word.split = ["Stay", "At", "USA"

                            if (len(partOfToken) == 0):
                                continue
                            if(not partOfToken.isdigit() and len(partOfToken) > 1): #For case: Stay
                                if(partOfToken[1].isupper()):
                                    finalWord+=partOfToken.upper()
                                    listOfTokens.insert(iIndex, partOfToken)
                                    iIndex+=1
                                #for case: "#Stay_At_Home" and "#stay_at_home"
                                else:
                                    finalWord+=partOfToken.lower()
                                    listOfTokens.insert(iIndex,partOfToken.lower())
                                    iIndex += 1
                            #for case: "#Covid_19" -> 19
                            else:
                                finalWord += partOfToken
                                listOfTokens.insert(iIndex, partOfToken)
                                iIndex += 1

                        listOfTokens[wordIndex] = finalWord #Now we changed: "#stay_at_home" to "#stayathome"

                    else:
                        #For case: "#StayAtHome"
                        wordToken = wordToken[1:] #wordToken = "StayAtHome"
                        listOfFinal = re.findall('[A-Z][^A-Z]*',finalWord) #listOfFinal = [Stay,At,U,S,A] || [Stay,At,Home]
                        correctWord = ""
                        for j in listOfFinal:
                            if(len(j) == 1):
                                jFollower=listOfFinal.index(j)+1
                                if(len(listOfFinal[jFollower]) == 1): #for case: USA
                                    correctWord = j
                                    while(len(listOfFinal[jFollower])==1):
                                        correctWord+=listOfFinal[jFollower]
                                        listOfFinal.remove(listOfFinal[jFollower])
                                    j = correctWord
                                #After: [Stay,At,USA]

                            else: # for "Stay"
                                j = j.lower() #from Stay -> stay
                            finalWord+=j
                            listOfTokens.insert(iIndex, j)
                            iIndex+=1
                    listOfTokens[wordIndex] = finalWord

                #for case: 10.6 precent
                if(wordToken == "precent" or wordToken == "precentage"):
                    wordTokenPlace=listOfTokens.index(j)
                    if(wordTokenPlace != 0):
                        listOfTokens[wordTokenPlace-1] += "%"
                        listOfTokens.remove(wordToken)

                #for case: 123 Thousand
                if(wordToken == "Thousand" or wordToken == "thousand" or wordToken == "Thousands" or wordToken == "thousands"):
                    thousandIndex = listOfTokens.index(wordToken)
                    if(thousandIndex!=0):

                        #for case: 123 Thousand (1-999)
                        if listOfTokens[thousandIndex-1].isnumeric():
                            listOfTokens[thousandIndex - 1] = listOfTokens[thousandIndex-1]+"K"
                            listOfTokens.remove(wordToken)

                        #for case: 123K Thousand
                        #if listOfTokens[thousandIndex-1][0:len(listOfTokens[thousandIndex-1])-1].isnumeric():
                        #    if():
                        #        listOfTokens[thousandIndex - 1] = listOfTokens[thousandIndex-1][0:len(listOfTokens[thousandIndex-1])-1] + "M"

                    #for case: Thousand -> 1K
                    else:
                        listOfTokens[thousandIndex] = "1K"

                #for case: 123 Million
                if(wordToken == "Million" or wordToken == "million" or wordToken == "Millions" or wordToken == "millions"):
                    millionIndex = listOfTokens.index(wordToken)
                    if(millionIndex!=0):

                        #for case: 123 Thousand (1-999)
                        if listOfTokens[millionIndex-1].isnumeric():
                            listOfTokens[millionIndex - 1] = listOfTokens[millionIndex-1]+"M"
                            listOfTokens.remove(wordToken)

                        #for case: 123K Thousand
                        #if listOfTokens[thousandIndex-1][0:len(listOfTokens[thousandIndex-1])-1].isnumeric():
                        #    if():
                        #        listOfTokens[thousandIndex - 1] = listOfTokens[thousandIndex-1][0:len(listOfTokens[thousandIndex-1])-1] + "M"

                    #for case: Thousand -> 1K
                    else:
                        listOfTokens[millionIndex] = "1M"

                #for case: 123 Billion
                if(wordToken == "Billion" or wordToken == "billion" or wordToken == "Billions" or wordToken == "billions"):
                    billionIndex = listOfTokens.index(wordToken)
                    if(billionIndex!=0):

                        #for case: 123 Billion (1-999)
                        if listOfTokens[billionIndex-1].isnumeric():
                            listOfTokens[billionIndex - 1] = listOfTokens[billionIndex-1]+"B"
                            listOfTokens.remove(wordToken)

                        #for case: 123K Thousand
                        #if listOfTokens[thousandIndex-1][0:len(listOfTokens[thousandIndex-1])-1].isnumeric():
                        #    if():
                        #        listOfTokens[thousandIndex - 1] = listOfTokens[thousandIndex-1][0:len(listOfTokens[thousandIndex-1])-1] + "M"

                    #for case: Billion -> 1B
                    else:
                        listOfTokens[billionIndex] = "1B"


                # for case: Numbers
                if (Parse.isfloat(wordToken.replace('.', '', 1))):
                    wordTokenNumber = float(wordToken)

                    # if there are more than 3 digit before the point
                    numberOfLoops = 0
                    varInt = ""
                    while wordTokenNumber / 1000 > 1:
                        wordTokenNumber /= 1000
                        numberOfLoops += 1

                    # Add K
                    if (numberOfLoops == 1):
                        varInt = "K"

                    # Add M
                    if (numberOfLoops == 2):
                        varInt = "M"

                    # Add B
                    if (numberOfLoops == 3):
                        varInt = "B"

                    listOfTokens[listOfTokens.index(wordToken)] = "%.3f" % round(wordTokenNumber, 3) + varInt

        #Change the words to Lower case or Upper Case
        for wordBeChange in listOfTokens:

            #for case: Max -> MAX/max
            if len(wordBeChange) > 1 and wordBeChange[0].isupper() and not wordBeChange[1].isupper():

                #for case: Max -> max
                if(wordBeChange.lower() in listOfTokens):
                    listOfTokens[listOfTokens.index(wordBeChange)] = wordBeChange.lower()

                #for case: Max -> MAX
                else:
                    listOfTokens[listOfTokens.index(wordBeChange)] = wordBeChange.upper()

        return listOfTokens


        def identifyTerms(queryTokens, docTokens): #----------------MOVE TO RANKER--------------------------
            term = ""
            termList=[]
            i = 0
            j = 0
            for i in queryTokens[i]:
                for j in docTokens[j]:
                    if(queryTokens[i] == docTokens[j]):
                        found = True
                        l=1
                        while(found):
                            if(queryTokens[i+l] == docTokens[j+l]):
                                term += queryTokens[i] + queryTokens[i+l]
                                l += 1
                                i += 1
                                j += 1
                            else:
                                found = False
                                termList.append(term)
            return termList



