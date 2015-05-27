import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import StandardScaler

import nltk.data
from bs4 import BeautifulSoup

from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords

import re

df = pd.read_csv('comment_table')
df.columns = ['body']
comments = df.values
clist = [str(c[0]) for c in comments]
cdf = pd.DataFrame(clist)
vect = CountVectorizer(stop_words='english')
counts = vect.fit_transform(clist)
counts.get_shape # 47732x24913
counts.sum(axis=1).mean() # 15.5 avg words per comment
counts.sum(axis=0).mean() # 30 avg occurences per word
comment_lengths = counts.sum(axis=1)
word_occurences = counts.sum(axis=0)
comment_lengths.mean() # 15.5 avg words per comment
word_occurences.mean() # 30

#make word_occurences an array for plotting
word_occurences = np.array(word_occurences).reshape(24913,)
feat_names = vect.get_feature_names()
feat_names[word_occurences.argmax()] # 'just'
feat_names[word_occurences.argmin()] # 00000000000001

# plt.hist(word_occurences, bins=100, log=True)
# plt.show()



stemmer = SnowballStemmer('english') # english stemmer is better than porter

def sentence_to_wordlist(sentence, remove_stopwords=False):
    # Function to convert a document to a sequence of words,
    # optionally removing stop words.  Returns a list of words.
    #
    # 1. Remove HTML
    sentence_text = BeautifulSoup(sentence).get_text()
    #  
    # 2. Remove non-letters
    sentence_text = re.sub("[^a-zA-Z]","", sentence_text) 
    #add \s to set to avoid splitting i'll into i and ll.
    # but this/or/that will become thisorthat
    
    # 3. Convert words to lower case and split them
    words = sentence_text.lower().split()
    #
    # 4. Optionally remove stop words (false by default)
    if remove_stopwords:
        stops = set(stopwords.words("english"))
        words = [w for w in words if not w in stops]
    #
    # 5. Return a list of words
    return words

def comment_to_sentences(comment, tokenizer, remove_stopwords=False ):
    """Split a comment into sentences, with each sentence split into words."""
    # Remove unicode that will break the tokenizer
    comment = comment.decode('raw_unicode_escape').encode('ascii', 'ignore')

    # Split comments into sentences
    raw_sentences = tokenizer.tokenize(comment)

    # Parse sentences, skip empty and deleted comments
    sentences = []
    for raw_sentence in raw_sentences:
        if len(raw_sentence) > 0 and raw_sentence != '[deleted]':
            sentences.append(comment_to_wordlist(raw_sentence, remove_stopwords))
    return sentences

def parse_comment_data(comment_corpus, tokenizer):
    """Convert a set of reddit comments into a cleaned format for Word2Vec."""
    # initialize sentence list
    sentences = []

    print "Generating sentences..."
    corpus_size = len(comment_corpus)
    count = 1
    for comment in comment_corpus:
        print "On comment %s of %s" % (count, corpus_size)
        sentences.extend(comment_to_sentences(comment, tokenizer))
        count += 1

    print "Generated %s sentences" % len(sentences)
    return sentences

sentence_detector = nltk.data.load('tokenizers/punkt/english.pickle')

# run word 2 vec

# Import the built-in logging module and configure it so that Word2Vec 
# creates nice output messages
import logging
from gensim.models import word2vec
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',\
    level=logging.INFO)

# Set values for various parameters
num_features = 300    # Word vector dimensionality                      
min_word_count = 40   # Minimum word count                        
num_workers = 4       # Number of threads to run in parallel
context = 5          # Context window size                                                                                    
downsampling = 1e-3   # Downsample setting for frequent words

# Initialize and train the model (this will take some time)

print "Training model..."
model = word2vec.Word2Vec(sentences_data, workers=num_workers, \
            size=num_features, min_count = min_word_count, \
            window = context, sample = downsampling)

"""# If you don't plan to train the model any further, calling 
# init_sims will make the model much more memory-efficient.
model.init_sims(replace=True)

# It can be helpful to create a meaningful model name and 
# save the model for later use. You can load it later using Word2Vec.load()
model_name = "300features_40minwords_10context"
model.save(model_name)"""

model.most_similar('riot')
model.most_similar('rito')
model.most_similar('rage')
model.most_similar('feed')
model.most_similar('win')
model.most_similar('ahri')
model.most_similar('assassin')

def main():

    # read in data
    df = pd.read_csv('comment_table')
    df.columns = ['body']
    comments = df.values
    clist = [str(c[0]) for c in comments]

    #explore a bit
    vect = CountVectorizer(stop_words='english')
    counts = vect.fit_transform(clist)
    counts.get_shape # 47732x24913
    counts.sum(axis=1).mean() # 15.5 avg words per comment
    counts.sum(axis=0).mean() # 30 avg occurences per word
    comment_lengths.mean() # 15.5 avg words per comment
    word_occurences.mean() # 30

    #take a look at sentence tokenizing
    sentence_tokenize(clist[0])
    sentence_tokenize(clist[1])
    sentence_tokenize(clist[2])
    sentence_tokenize(clist[3])
    sentence_tokenize(clist[4])
    sentence_tokenize(clist[5])
    sentence_tokenize(clist[6])
    sentence_tokenize(clist[7])
    sentence_tokenize(clist[8])
    sentence_tokenize(clist[9])
    sentence_tokenize(clist[10])
    sentence_tokenize(clist[11])
    sentence_tokenize(clist[12])