import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import StandardScaler
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

plt.hist(word_occurences, bins=20, log=True)
plt.show()