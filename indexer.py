import re
import collections
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import cPickle
from flask import Flask, request, jsonify, render_template, url_for, redirect
from flask_restful import Resource, Api

app = Flask(__name__)

stopwordslist = stopwords.words("english")
stemmer = PorterStemmer()

file_list = []
file_list.append(open("Demon haunted world Carl Sagan.txt","r"))
file_list.append(open("Hacker Monthly - Issue 26.txt","r"))
file_list.append(open("Stephen Hawking, His Life And Work.txt","r"))
file_list.append(open("The_Grand_Design.txt","r"))
file_list.append(open("The Universe and Dr Einstein.txt","r"))

def words(text): return re.findall('[a-z]+', text.lower()) 

def train(features):
    model = collections.defaultdict(lambda: 1)
    for f in features:
        model[f] += 1
    return model

data =  file("The Universe and Dr Einstein.txt").read() + file("The_Grand_Design.txt").read() + file("Stephen Hawking, His Life And Work.txt").read() + file("Demon haunted world Carl Sagan.txt").read() + file("Hacker Monthly - Issue 26.txt").read()
NWORDS = train(words(data))

alphabet = 'abcdefghijklmnopqrstuvwxyz'

def edits1(word):
   splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
   deletes    = [a + b[1:] for a, b in splits if b]
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
   inserts    = [a + c + b     for a, b in splits for c in alphabet]
   return set(deletes + transposes + replaces + inserts)

def known_edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)

def known(words): return set(w for w in words if w in NWORDS)

def correct(word):
    candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word]
    return max(candidates, key=NWORDS.get)

def remove_unicode(data):
    return data.decode('unicode_escape').encode('ascii','ignore')

def clean_document(data):
    data = re.sub(r'\W+', ' ', data)
    return re.sub( '\s+', ' ', data).strip()

def to_lower(data):
    return data.lower()

def distinct_words(data):
    words = data.split()
    word_occured_map = {}
    word_ret = []

    for word in words:
        if word not in word_occured_map:
            word_occured_map[word] = 1
            word_ret.append(word)

    return  word_ret

def remove_stopwords(words):
    return [word for word in words if word not in stopwordslist]

def stemming(words):
    word_occured_map = {}
    word_ret = []

    for word in words:
        word = stemmer.stem(word)
        if word not in word_occured_map:
            word_occured_map[word] = 1
            word_ret.append(word)

    return  word_ret

def diff(list1, list2):
    c = set(list1).union(set(list2))
    d = set(list1).intersection(set(list2))
    return list(c - d)

index = {}
map_index_to_doc_name = {1:'Demon haunted world Carl Sagan',2:'Hacker Monthly - Issue 26',3:'Stephen Hawking, His Life And Work.txt',4:'The_Grand_Design.txt',5:'The Universe and Dr Einstein'}

file_no = 1
for file_pointer in file_list:
    data = file_pointer.read()
    data = remove_unicode(data)
    data = clean_document(data)
    data = to_lower(data)
    words = distinct_words(data)
    words = remove_stopwords(words)
    words = stemming(words)

    for word in words:
        if word not in index:
            index[word] = [file_no]
        else:
            index[word].append(file_no)

    file_no += 1

cPickle.dump(index, open('index.p','wb'))
index = cPickle.load(open('index.p','rb'))


@app.route('/search', methods=['POST'])
def my_search():
    query = request.form['query']
    query = clean_document(query)
    query = to_lower(query)

    words = query.split()

    correct_words = []
    for word in words:
        correct_words.append(correct(word))

    words = [stemmer.stem(word) for word in correct_words]
    
    lst_remove = []
    i = 0
    while i < len(words):
        if words[i] != 'and' and words[i] != 'or':
            if words[i] == 'not':
                if words[i+1] in index:
                    words[i+1] = diff([1,2,3,4,5],index[words[i+1]]) 
                else:
                    words[i+1] = diff([1,2,3,4,5],[])
                lst_remove.append(i)
                i += 1
            else:
                if words[i] in index:
                    words[i] = index[words[i]]
                else:
                    words[i] = []
        i += 1
    
    i = 0  
    for item in lst_remove:
        words.pop(item - i)
        i += 1

    while len(words) > 1:
        if words[1] == 'or':
            words[0] = (set(words[0]).union(set(words[2])))
            words.pop(1)
            words.pop(1)
        elif words[1] == 'and':
            words[0] = (set(words[0]).intersection(set(words[2])))
            words.pop(1)
            words.pop(1)

    result = [' '.join(correct_words)]
    for doc_no in words[0]:
        print map_index_to_doc_name[doc_no]
        result.append(map_index_to_doc_name[doc_no])

    return jsonify({'result':result})

@app.route('/')
def my_index():
    return render_template('index.html')

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=8080)
    app.run(debug=True)