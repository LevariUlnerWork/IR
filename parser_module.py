import calendar
import re
from document import Document


class Parse:

    def __init__(self, stemming=None, iIndexer=None, invIdx = None):
        #self.stop_words = stopwords.words('english') - we are not use this stop words
        full_path = open('stop-words.txt',"r")
        listOfStopWords = full_path.read()
        self.stemmering = stemming
        #print(listOfStopWords)
        full_path.close()
        self.stop_words = listOfStopWords.split(" ")
        self.invIdx = None
        if(iIndexer != None):
            self.invIdx = iIndexer.inverted_idx
        elif(invIdx != None):
            self.invIdx = invIdx

        #print(type(self.stop_words))


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
        text_tokens_without_stopwords = [w for w in text_tokens if w not in self.stop_words]


        #capital and lower letters
        for wordInx in range(len(text_tokens_without_stopwords)):
            word = text_tokens_without_stopwords[wordInx]
            if len(word) > 1 and word[0].isupper() and ' ' not in word and '-' not in word:
                # for case: Max -> max
                if (word.lower() in self.invIdx[3].keys()):
                    word = word.lower()
                    text_tokens_without_stopwords[wordInx] = word
                # for case: Max -> MAX
                else:
                    word = word.upper()
                    text_tokens_without_stopwords[wordInx] = word

        if (self.stemmering != None):
            text_tokens_without_stopwords = self.stemmering.stem_list(text_tokens_without_stopwords)

        #EntityRecognition:
        text = text.encode("ascii", "ignore").decode()  # delete all illegal characters like emojis
        text_before_parse = text.split(' ')
        real_index_word = 0
        for index_word in range(len(text_before_parse)):
            word = text_before_parse[index_word]
            if(index_word < real_index_word): #is there index that smaller than 0
                continue
            if(len(word) > 1 and (word[0].isupper() or '-' in word or '_' in word) and ('.' not in word and  ',' not in word and '?' not in word and '!' not in word and ':' not in word)): #for Max Rossenfield
                next_index = index_word + 1
                while (next_index < len(text_before_parse) and len(text_before_parse[next_index]) > 1 and text_before_parse[next_index][0].isupper()):
                    stopHere = False
                    next_word = text_before_parse[next_index]
                    if('.' in next_word or ',' in next_word or '?' in next_word or '!' in next_word or ':' in next_word): #If we should stop
                        stopHere = True
                        if('.' in next_word):
                            next_word = next_word.split('.')[0]
                        if(',' in next_word):
                            next_word = next_word.split('.')[0]
                        if('?' in next_word):
                            next_word = next_word.split('.')[0]
                        if('!' in next_word):
                            next_word = next_word.split('.')[0]
                        if (':' in next_word):
                            next_word = next_word.split('.')[0]
                    else:
                        next_word = next_word

                    # Donald Trump | "Alexandria Ocasio-Cortez"
                    word += " " + next_word
                    real_index_word += 1
                    next_index += 1

                    if(stopHere == True):
                        break

                if(' ' in word or '-' in word):
                    text_tokens_without_stopwords.insert(index_word, word)

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
        indices = doc_as_list[4]
        retweet_text = doc_as_list[5]
        retweet_url = doc_as_list[6]
        retweet_url_indices = doc_as_list[7]
        quote_text = doc_as_list[8]
        quote_url = doc_as_list[9]
        quote_url_indices = doc_as_list[10]
        retweet_quoted_text = doc_as_list[11]
        retweet_quoted_url = doc_as_list[12]
        retweet_quoted_indices = doc_as_list[13]
        term_dict = {}

        #isit = self.parse_sentence("y'all") #to check ourselves texts
        #TODO: delete terms: '/-', "\'","\" , 132,000+, "𝑩𝒓𝒆𝒂𝒌𝒊𝒏𝒈: 𝑯𝒖𝒔𝒉𝒑𝒖𝒑𝒑𝒊 𝒉𝒂𝒔 𝒕𝒆𝒔𝒕𝒆𝒅 𝒑𝒐𝒔𝒊𝒕𝒊𝒗𝒆 𝒇𝒐𝒓 𝑪𝒐𝒗𝒊𝒅-19 𝒊𝒏 𝒑𝒓𝒊𝒔𝒐𝒏."


        #creating the real fields:
        #start with urls:
        old_ulrs = [url,retweet_url,quote_url,retweet_quoted_url]
        new_urls=[]
        for realUrlText in old_ulrs:
            realUrlList=[]
            if type(realUrlText) == str and len(realUrlText) > 2: #url {} was added
                realUrlList = realUrlText.split(':') # realUrlList = {https, //t.co.. , https, //www.twitter.com...}
            real_url_text=""
            if(len(realUrlList) == 4):
                real_url_text = realUrlList[2] + ":" + realUrlList[3]
                real_url_text = real_url_text.replace('}' , '')
                real_url_text = real_url_text.replace('"', '')
            new_urls.append(real_url_text)
        url,retweet_url,quote_url,retweet_quote_url = new_urls # url = https:... retweet_url = https...

        #fix texts:
        texts_list = [full_text, retweet_text, quote_text, retweet_quoted_text]
        url_list = [url,retweet_url,quote_url,retweet_quote_url]
        indices_list = [indices,retweet_url_indices,quote_url_indices,retweet_quoted_indices]
        i=0
        for ind in indices_list: # ind = null | = [] | = [[120,143]]
            if(type(ind) == str and len(ind) > 2):
                stopPoint = ind.split(',')[0].replace('[', '')
                if("http" in texts_list[i][int(stopPoint):]):
                    texts_list[i] = texts_list[i][:int(stopPoint)] + url_list[i]
                else:
                    texts_list[i]+=url_list[i]
            i+=1
        full_text, retweet_text, quote_text, retweet_quoted_text = texts_list


        try: #trying to parse the text, if it failed - we loose the term of this tweet, but the IR continues
            tokenized_text = []
            if("RT" not in full_text):
                tokenized_text = self.parse_sentence(full_text)
            if(type(retweet_text) == str and len(retweet_text)!= ''):
                tokenized_text += self.parse_sentence(retweet_text)
            if (type(quote_text) == str and len(quote_text)!= ''):
                tokenized_text += self.parse_sentence(quote_text)
            if (type(retweet_quoted_text) == str and len(retweet_quoted_text) != ''):
                tokenized_text += self.parse_sentence(retweet_quoted_text)

        except:
            tokenized_text = []


        doc_length = len(tokenized_text)  # after text operations.

        #Do Captial letters here
        index= 0
        for term in tokenized_text: #termDict:{key=term:[[indexes],freq]

            if(term == "t.co" or term == "https"): #think about more words
                continue

            if term not in term_dict.keys():
                term_dict[term] = [[index],1]
            else:
                term_dict[term][1] += 1
                term_dict[term][0].append(index)
            index += 1

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length)
        return document

    #Punctuation
    def punctuation(text):
        # if (('?' or '(' or ')' or '[' or ']' or '{' or '}' or "\n" or "\t" or "\'" or imojis or ':' or ';' or '!' or "'") in text):
        text = text.replace('?', ' ')
        text = text.replace('!', ' ')
        text = text.replace('&', ' ')
        text = text.replace(';', ' ')
        text = text.replace(':', ' ')
        text = text.replace('"', ' ')
        text = text.replace('(', ' ')
        text = text.replace(')', ' ')
        text = text.replace('[', ' ')
        text = text.replace(']', ' ')
        text = text.replace('{', ' ')
        text = text.replace('}', ' ')
        text = text.replace('\n', ' ')
        text = text.replace('\t', ' ')
        text = text.replace("//", '')
        text = text.replace("_", " ")
        text = text.replace("\'", "'")
        text = text.replace("’", "'")


        listWithoutPunc = text.split(' ')


        #this list is not final
        #punctuationList = [' ','&',';','(',')','[',']','{','}','?','!', '"' , ':'] #ignore them=

        for word in listWithoutPunc:
            numIndex = listWithoutPunc.index(word)

            #check shortcuts
            shortcutDict = {"ain't": "am not / are not","aren't": "are not / am not","can't": "cannot","can't've": "cannot have",
                             "'cause": "because","could've": "could have","couldn't": "could not","couldn't've": "could not have",
                             "didn't": "did not","doesn't": "does not","don't": "do not","hadn't": "had not","hadn't've": "had not have",
                             "hasn't": "has not","haven't": "have not","he'd": "he had / he would","he'd've": "he would have",
                             "he'll": "he shall / he will","he'll've": "he shall have / he will have","here's":"here is" ,"he's": "he has / he is",
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

            if word.lower() in shortcutDict.keys():
                listWithoutPunc.pop(numIndex)
                i = numIndex
                word = shortcutDict[word.lower()]
                toJump = False
                for term in word.split(' '):
                    if('/' != term):
                        listWithoutPunc.insert(i, term)
                        word = term
                        i+=1
                        toJump = True
                if(toJump):
                    continue

            word = word.replace("'", "")

            #checkPowerScript
            shortscriptDict = {"⁰":"0","¹":"1","²":"2","³":"3","⁴":"4","⁵":"5" ,"⁶":"6","⁷":"7","⁸":"8","⁹":"9",
                               "ᵃ":"a","ᵇ":"b","ᶜ":"c","ᵈ":"d","ᵉ":"e","ᶠ":"f","ᵍ":"g","ʰ":"h","ᶦ":"i","ʲ":"j",
                               "ᵏ":"k","ˡ":"l","ᵐ":"m","ⁿ":"n","ᵒ":"o","ᵖ":"p","۹":"q","ʳ":"r","ˢ":"s","ᵗ":"t",
                               "ᵘ":"u","ᵛ":"v","ʷ":"w","ˣ":"x","ʸ":"y","ᶻ":"z","ᴬ":"A","ᴮ":"B","ᴰ":"D",
                               "ᴱ":"E","ᴳ":"G","ᴴ":"H","ᴵ":"I","ᴶ":"J","ᴷ":"K","ᴸ":"L","ᴹ":"M","ᴺ":"N",
                               "ᴼ":"O","ᴾ":"P","Q":"Q","ᴿ":"R","ᵀ":"T","ᵁ":"U","ⱽ":"V","ᵂ":"W",
                               "⁺":"+","⁻":"-","⁼":"=","⁽":"(","⁾":")"}

            listOfPow = list(word)
            realWord = ""
            for pow in listOfPow:
                if pow in shortscriptDict.keys():
                   realWord += shortscriptDict[pow]
                else:
                    realWord += pow

            listWithoutPunc.pop(numIndex)
            listWithoutPunc.insert(numIndex, realWord)
            word = realWord
            word = word.encode("ascii", "ignore").decode()  # delete all illegal characters like emojis --------AGAIN?
            listWithoutPunc[numIndex] = word
            if('.' in word or ',' in word or '/' in word or '-' in word):
                if (word == ',' or word == '.' or word == '/' or word == '-'):
                    listWithoutPunc.pop(numIndex)
                    continue
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
                        if ('-' in word): #321-312
                            wordList = word.split('-')
                            listWithoutPunc[numIndex] = wordList[0]
                            for i in range (1,len(wordList)):
                                listWithoutPunc.insert(numIndex+i, wordList[i])
                        else: # 123.33 | 213/2312
                            continue

                    elif (len(seperateWordList) >= 2):
                        # for case: go. | go,
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
                            if (i=='.' and '/' in word and '.' in word):
                                continue
                            # for case: "His/Her | his,her"
                            listWithoutPunc.pop(numIndex)
                            place = numIndex
                            for w in seperateWordList:
                                if("www" in w):
                                    listWithoutPunc.insert(place, "www")
                                    w = w[4:]
                                    place += 1
                                listWithoutPunc.insert(place,w)
                                place+=1
                            word = listWithoutPunc[numIndex]
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
        return listWithoutPunc

    def isfloat(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def tokenize_words(text):
        listOfTokens = Parse.punctuation(text)

        for wordIndex in range(0,len(listOfTokens)):

            wordToken= listOfTokens[wordIndex]

            if(len(wordToken) > 0):

                #tags
                if(wordToken[0] == '@' and len(wordToken) != 1):
                    listOfTokens.insert(wordIndex ,"@")
                    wordIndex += 1
                    listOfTokens[wordIndex] = wordToken[1:] #should be wordIndex+1 ???????????????????????????????????
                    continue

                #dollar
                if('$' in wordToken):
                    listOfTokens.insert(wordIndex+1, "dollar") #why +1 ?????????????????????????????????????????????????????
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
                            #if(not partOfToken.isdigit() and len(partOfToken) > 1): #For case: Stay
                            if (not partOfToken.isdigit()):  # For case: Stay
                                #if(partOfToken[1].isupper()):#IF STay -> STAY
                                 #   finalWord+=partOfToken.upper()
                                 #  listOfTokens.insert(iIndex, partOfToken)
                                 #   iIndex+=1
                                #for case: "#Stay_At_Home" and "#stay_at_home"
                                #else: # if: Stay -> stay
                                 finalWord+=partOfToken.lower()
                                 listOfTokens.insert(iIndex,partOfToken.lower())
                                 iIndex += 1
                            #for case: "#~Covid_~19" -> 19
                            else:
                                finalWord += partOfToken
                                listOfTokens.insert(iIndex, partOfToken)
                                iIndex += 1

                        listOfTokens[wordIndex] = finalWord #Now we changed: "#stay_at_home" to "#stayathome"

                    else:
                        #For case: "#StayAtHome"
                        wordToken = wordToken[1:] #wordToken = "StayAtHome"
                        listOfFinal = re.findall('[A-Z][^A-Z]*',wordToken) #listOfFinal = [Stay,At,U,S,A] || [Stay,At,Home]
                        correctWord = ""
                        if len(listOfFinal)==0:
                            listOfFinal = [wordToken]
                        for j in listOfFinal:
                            if(len(j) == 1):
                                jFollower=listOfFinal.index(j)+1
                                if(jFollower < len(listOfFinal) and len(listOfFinal[jFollower]) == 1): #for case: USA
                                    correctWord = j
                                    while(jFollower < len(listOfFinal) and len(listOfFinal[jFollower])==1 and listOfFinal[jFollower][0].isupper()):
                                        correctWord+=listOfFinal[jFollower]
                                        listOfFinal.remove(listOfFinal[jFollower])

                                    if (jFollower < len(listOfFinal) and listOfFinal[jFollower][0].isupper()):
                                        correctWord += listOfFinal[jFollower][0]
                                        listOfFinal[jFollower]= listOfFinal[jFollower][1:]
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
                    if(wordIndex != 0):
                        listOfTokens[wordIndex-1] += "%"
                        listOfTokens.pop[wordIndex]

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
                if (Parse.isfloat(wordToken.replace('.', '', 1))): # if the word is like "inf" or "infinity" it would false positivily think it is a number
                    wordTokenNumber = float(wordToken)
                    if(wordTokenNumber > 1000000000000):
                        continue
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

                    listOfTokens[wordIndex] = "%.3f" % round(wordTokenNumber, 3) + varInt

                #for case: 6 3/4 and date
                if("/" in wordToken):
                    #for case: 6 3/4
                    if(listOfTokens[wordIndex-1].isdigit()):
                        listOfTokens[wordIndex-1] += " " + wordToken
                        listOfTokens.pop(wordIndex)
                    else: #3/4 -> 3th at April
                        dateNum = wordToken.split('/')
                        if(len(dateNum)>3 or int(dateNum[0]) > 31 or int(dateNum[1]) > 31 or (int(dateNum[0]) > 12 and int(dateNum[1]) > 12)):
                            continue
                        if(int(dateNum[1]) > 12):
                            day = dateNum[1]
                            month = calendar.month_abbr[int(dateNum[0])];
                        else:
                            day = dateNum[0]
                            month = calendar.month_abbr[int(dateNum[1])];
                        if(day == "1"):
                            day+="st"
                        if(day == "2"):
                            day+= "nd"
                        if(day == "3"):
                            day += "rd"
                        else:
                            day += "th"
                        listOfTokens[wordIndex] = day
                        wordIndex+=1
                        listOfTokens.insert(wordIndex, month)
                        wordToken = month
                        if(len(dateNum) == 3):
                            year = dateNum[2]
                            wordIndex += 1
                            listOfTokens.insert(wordIndex,year)
                            wordToken = year


        while '' in listOfTokens:
            listOfTokens.remove('')
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



