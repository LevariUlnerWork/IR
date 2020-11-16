import os
import re
from nltk.stem import PorterStemmer
#from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
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

    #This function is used for queries and tweets
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

        listWithoutPunc = text.split(' ')
        #domain=""
        domain=[]
        # for case:www.abc.com -> URL
        if 'https://' in text:
            for word in listWithoutPunc:
                if ('https://' in word):
                    domain = word.split('//')  # domain = [{"https:", "t.co/sdfs..."]
                    domain = domain[1].split('/')  # domai = ["t.co", "sdfs"...]
                    domain = domain[0]  # domain = "t.co"


        #this list is not final
        #punctuationList = [' ','&',';','(',')','[',']','{','}','?','!', '"' , ':'] #ignore them=

        #I delete this because it changes nothing:
        #if (('?' or '(' or ')' or '[' or ']' or '{' or '}') in text):
        #    for word in listWithoutPunc:
        #        word.replace('?', '')
        #        word.replace('(', '')
        #        word.replace(')', '')
        #        word.replace('[', '')
        #        word.replace(']', '')
        #        word.replace('{', '')
        #        word.replace('}', '')
        for word in listWithoutPunc:
            if("https" not in word):
                numIndex = listWithoutPunc.index(word)
                #if (('?' or '(' or ')' or '[' or ']' or '{' or '}' or "\n" or "\t" or "\'" or '😉' or ':' or ';' or '!' or "'") in text):
                word = word.replace('?','')
                word = word.replace('!', '')
                word = word.replace('&', '')
                word = word.replace(';', '')
                word = word.replace(':', '')
                word = word.replace("'", '')
                word = word.replace('(', '')
                word = word.replace(')', '')
                word = word.replace('[', '')
                word = word.replace(']', '')
                word = word.replace('{', '')
                word = word.replace('}', '')
                word = word.replace('\n', '')
                word = word.replace('\t', '')
                word = word.replace("\'", '') # for case: D\'ont -> Dont
                word = word.encode("ascii","ignore").decode() # delete all illegal characters like emojies
                listWithoutPunc[numIndex] = word
                wordBeforeChange = word


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
                                wordBeforeChange = word
                            else:
                                # for case: "His/Her | his,her"
                                listWithoutPunc.pop(numIndex)
                                listWithoutPunc += seperateWordList
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
        for wordToken in listOfTokens:
            #if('\' in wordToken): ----------------------CHECK-------------------------------

            if(len(wordToken) > 0):
                #tags
                if(wordToken[0] == '@' and len(wordToken)!=1):
                    listOfTokens.append("@")
                    listOfTokens.append(wordToken[1:])

                #Hashtags
                if (wordToken[0] == '#' and not wordToken[1:].isdigit()):

                    finalWord = "#"  # Final Word: "#stayathome"
                    if(wordToken.find("_") != -1):# if there is a '_'
                        wordToken = wordToken[1:] #now: "stay_at_home"
                        #For case: "#Stay_At_Home" and "#stay_at_home"
                        for partOfToken in wordToken.split('_'):
                            #For case: "Stay_At_USA"
                            if (len(partOfToken) == 0):
                                continue
                            if(not partOfToken.isdigit()):
                                if(partOfToken[1].isupper()): #TODO: call for number too
                                    finalWord+=partOfToken.upper()
                                    listOfTokens.append(partOfToken)
                                #for case: "#Stay_At_Home" and "#stay_at_home"
                                else:
                                    finalWord+=partOfToken.lower()
                                    listOfTokens.append(partOfToken.lower())
                            #for case: "#Covid_19" -> 19
                            else:
                                finalWord += partOfToken
                                listOfTokens.append(partOfToken)

                        listOfTokens[listOfTokens.index("#"+wordToken)] = finalWord #Now we changed: "#stay_at_home" to "#stayathome"

                    else:
                        #For case: "#StayAtHome"
                        firstWord = wordToken
                        wordToken = wordToken[1:] #Remove '#'
                        listOfFinal = re.findall('[A-Z][^A-Z]*',finalWord) #listOfFinal = [Stay,At,U,S,A] || [Stay,At,Home]
                        correctWord = ""
                        for j in listOfFinal:
                            if(len(listOfFinal) == 1):
                                listOfFinal.append(j)
                            if(len(j) == 1):
                                jFollower=listOfFinal.index(j)+1
                                if(len(listOfFinal[jFollower]) == 1): #for case: USA
                                    correctWord = j
                                    while(len(listOfFinal[jFollower])==1):
                                        correctWord+=listOfFinal[jFollower]
                                        listOfFinal.remove(listOfFinal[jFollower])
                                    listOfFinal.append(correctWord)
                                #After: [Stay,At,USA]

                            else: # for "Stay"
                                listOfFinal[listOfFinal.index[j]] = j.lower() #from Stay -> stay

                        listOfTokens+=listOfFinal


                        for i in listOfFinal:
                            partOfToken.append(i.lower())
                        listOfTokens[listOfTokens.index(firstWord)] = finalWord

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

                """
                #I deleted it because all the numbers were... dates!
                #for case: 3/4 and 6 3/4
                if("/" in wordToken):
                    numerator = wordToken[:wordToken.find("/")]
                    denominator = wordToken[wordToken.find("/")+1:]
                    if(not (Parse.isfloat(numerator) and Parse.isfloat(denominator))):
                        continue
                    wordNumber = float(numerator) / float(denominator)

                   #for case: 6 3/4
                    wordBefore = listOfTokens[listOfTokens.index(wordToken) - 1]
                    if Parse.isfloat(wordBefore):
                        #6 3/4 -> 6.75
                        beforNumber = float(listOfTokens[listOfTokens.index(wordToken)-1])+wordNumber
                        listOfTokens[listOfTokens.index(wordToken) - 1] = str(beforNumber)
                        listOfTokens.remove(wordToken)
                        # Now the new number is the token, so it would enter to the Number case
                        wordToken=str(beforNumber)

                    #for case: 6K 3/4 // 6M 3/4 // 6B 3/4 --------------------------- CHECK-------------------------
                    if Parse.isfloat(wordBefore[:len(wordBefore) - 1] and (wordBefore[len(wordBefore) - 1] == "K" or wordBefore[len(wordBefore) - 1] == "M" or wordBefore[len(wordBefore) - 1] == "B")):
                        beforNumber = int(listOfTokens[listOfTokens.index(wordToken) - 1]) + wordNumber
                        if(wordBefore[len(wordBefore) - 1] == "K"):
                            beforNumber *= 1000
                        if(wordBefore[len(wordBefore) - 1] == "M"):
                            beforNumber *= 1000000
                        if(wordBefore[len(wordBefore) - 1] == "B"):
                            beforNumber *= 1000000000
                        listOfTokens[listOfTokens.index(wordToken) - 1] = str(beforNumber)
                        listOfTokens.remove(wordToken)
                        # Now the new number is the token, so it would enter to the Number case
                        wordToken = str(beforNumber)

                    #for case: 3/4
                    else:
                        listOfTokens[listOfTokens.index(wordToken)] = str(wordNumber)
                """
                # for case: Numbers
                if (wordToken.replace('.', '', 1).isdigit()):
                    if(("₀" or "₁" or "₂" or "₃" or "₄" or "₅" or "₆" or "₇" or "₈" or "₉") in wordToken): #Should replace subscript
                        wordToken = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
                    if(("⁰" or "¹" or "²" or "³" or "⁴" or "⁵" or "⁶" or "⁷" or "⁸" or "⁹") in wordToken):#Should replace superscript
                        wordToken = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
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



