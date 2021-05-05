import spacy
import sys
import random
from classes.question import Question
from collections import Counter
from string import punctuation
from gensim.models import KeyedVectors
from gensim.scripts.glove2word2vec import glove2word2vec
import re


filename = sys.argv[1]
nbwords = 0

#load spacy model
nlp = spacy.load("en_core_web_trf")


glove_file = './data/embeddings/glove.6B.100d.txt'
tmp_file = './data/embeddings/word2vec-glove.6B.100d.txt'

model = KeyedVectors.load_word2vec_format(tmp_file)
print("Model loaded", flush=True)

# load text function
def load_text(filename):
    with open(filename, 'r') as file:
        text = file.read()
    text = text.replace('\n', ' ')
    return text


#hotword function
def get_hotwords(text):
    result = []
    pos_tag = ['PROPN', 'ADJ', 'NOUN', 'NUM'] # 1
    doc = nlp(text) # 2
    for token in doc:
        # 3
        if(token.text in nlp.Defaults.stop_words or token.text in punctuation):
            continue
        # 4
        if(token.pos_ in pos_tag):
            result.append(token.text)

    return result # 5

def get_entities(text):
    result = {}
    doc = nlp(text)
    accept_ent = ['NORP', 'DATE', 'TIME', 'ORDINAL', 'CARDINAL']
    for ent in doc.ents:
        print('[',ent.label_ , '(', spacy.explain(ent.label_),") ] " , ent.text)
        if(ent.label_ in accept_ent):
            result[ent.text] = ent.label_
    return result



def replace_kwords(text, keywords):
    keywods =  sorted(keywords, key=len, reverse=True)
    text = ' ' + text
    i = 0
    for word in keywords:
        nword = ' ' + word + ' '
        text = text.replace(nword, " _" + str(i) +  "_ ", 1)
        nword = ' ' + word + '.'
        text = text.replace(nword, " _" + str(i) +  "_.", 1)
        nword = ' ' + word + ','
        text = text.replace(nword, " _" + str(i) +  "_,", 1) 
        nword = ' ' + word + '-'
        text = text.replace(nword, " _" + str(i) +  "_-", 1) 
        i = i+1
    text = text[1:]
    return text


def generate_distractors(keywords):
    options = []
    answers = []
    for k,v in keywords.items():
        print ("key = ", k, " - value = ", v) 
        option = [str(k)]
        similar  = []
        if (v == 'ORDINAL'):
            similar = model.most_similar(positive=[str(k)], topn=3)
        elif (v == 'CARDINAL'):
            similar = model.most_similar(positive=[str(k)], topn=3)
        elif (v == 'NORP'):
            similar = model.most_similar(positive=[str(k).lower()], topn=3)
            option = []
            t = k.lower()
            print(t)
            option = [t]
        elif (v == 'TIME'):
            
            regexp = re.compile('([0-1]?[0-9]|2[0-3]):[0-5][0-9]')
            regexp2 = re.compile('([0-5][0-9]|[1-9])')
            if regexp.search(str(k)):

                stringtorep = str(k)
                
                h = random.randint(0,23)
                m = random.randint(0,59)
                repl = str(h) + ':' + str(f'{m:02d}')
                ret  = re.sub('([0-1]?[0-9]|2[0-3]):[0-5][0-9]', repl, stringtorep)
                
                h = random.randint(0,23)
                m = random.randint(0,59)
                repl = str(h) + ':' + str(f'{m:02d}')
                ret2  = re.sub('([0-1]?[0-9]|2[0-3]):[0-5][0-9]', repl, stringtorep)
            
                similar = [(ret,11), (ret2, 22)]
            elif regexp2.search(str(k)):
                stringtorep = str(k)
                
                m = random.randint(0,59)
                repl = str(m)
                ret  = re.sub('([0-5][0-9]|[1-9])', repl, stringtorep)
                m = random.randint(0,59)
                repl = str(m)
                ret2  = re.sub('([0-5][0-9]|[1-9])', repl, stringtorep)

                similar = [(ret,11), (ret2, 22)]

            else:
                similar = [('test1',11), ('test2', 22)]
        elif (v == 'DATE'):
            regexp  = re.compile('( [1-9] | [12]\d | 3[01] )')
            regexp2 = re.compile('( [1-9],| [12]\d,| 3[01],)')
            nk = ' ' + str(k) + ' '
            if regexp.search(nk):
                print("matched 1")
                day = random.randint(1,31)
                ret = re.sub('( [1-9] | [12]\d | 3[01] )', ' ' +str(day) + ' ', nk)
                day = random.randint(1,31)
                ret2 = re.sub('( [1-9] | [12]\d | 3[01] )',' ' +str(day) + ' ', nk)
                print("ret2 : ", ret2)
                similar = [(ret[1:],11), (ret2[1:], 22)]
            elif regexp2.search(nk): 
                print("matched 2")
                day = random.randint(1,31)
                ret = re.sub('( [1-9],| [12]\d,| 3[01],)', ' ' +str(day) + ',', nk)
                day = random.randint(1,31)
                ret2 = re.sub('( [1-9],| [12]\d,| 3[01],)',' ' +str(day) + ',', nk)
                similar = [(ret[1:],11), (ret2[1:], 22)]
            else :
                similar = [('date1',11), ('date2', 22)]
        else  :
            similar = [('test1',11), ('test2', 22)]
        for item in similar:
                option.append(str(item[0]))
        ans = option[0]
        random.shuffle(option)
        print ("Options : " ,option)
        print("Index of answer is : ", option.index(ans))
        answers.append(option.index(ans))
        options.append(option)
    return [options, answers]

"""text = load_text(filename)
# get hot words and remove keywords
nbwords = int(len(text.split())*0.06)
output = get_hotwords(text)
entities = get_entities(text)
print("text : ", text, "\nnbwords = ", nbwords , "\n keywords = ", output)
print("entities : ", entities)
keywords = {}

#for i in range (len(output)):
#    if (output[i] in get_entities(text)):
#        keywords.append(output[i])

keywords = entities
if len(keywords) > nbwords:
    keywords = random.sample(keywords, nbwords)

#if len(keywords) < nbwords:
#    keywords = keywords  + random.sample(output,nbwords - len(keywords))


print(keywords)
generate_distractors(keywords)
replace_kwords(text, keywords)
"""

def generate(text):
    
    nbwords = int(len(text.split())*0.06)
    output = get_hotwords(text)
    entities = get_entities(text)
    print("text : ", text, "\nnbwords = ", nbwords , "\n keywords = ", output)
    print("entities : ", entities)
    keywords = entities
   
    nkeywords = {}
    if len(keywords) > nbwords:
        i  = 0
        for k,v in keywords.items():
            nkeywords[k] = v
            i = i+1
            if (i > nbwords):
                break
        keywords = nkeywords
    #if len(keywords) > nbwords:
    #    keywords = random.sample(sorted(keywords), nbwords)

    print("Keywords : ", keywords)
    gap_text = replace_kwords(text, keywords)
    [options, answers] = generate_distractors(keywords)


    #Création de la liste de questions
    questions_list_Aik = []
   
    for i in range(len(options)):
        print("Generating question :", str(i))
        gap_text_n = gap_text + "\nAnswer gap n°" + str(i) 
        q = Question(gap_text_n, options[i], answers[i])
        questions_list_Aik.append(q)


    return questions_list_Aik
