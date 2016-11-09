
# coding: utf-8

import nltk
 
# - $p_j^i$ 
# - ngram 任何位置不包含符號
# - skip bigram 不包含 stop words 與數字

from __future__ import division

k0 = 1
k1 = 1
U0 = 10
max_distance = 5

from nltk.tokenize import  wordpunct_tokenize 
from nltk.corpus import stopwords 

eng_stopwords = set(stopwords.words('english'))
eng_symbols = '{}"\'()[].,:;+!?-*/&|<>=~$'

def ngram_is_valid(ngram):
    first, last = ngram[0], ngram[-1]
    if first in eng_stopwords or last in eng_stopwords: return False
    if any( num in first or num in last for num in '0123456789'): return False
    if any( eng_symbol in word for word in ngram for eng_symbol in eng_symbols): return False
    return True

from collections import defaultdict, Counter
from itertools import izip

def to_ngrams( unigrams, length):
    return izip(*[unigrams[i:] for i in range(length)])  

from nltk.tokenize import  wordpunct_tokenize 

ngram_counts = defaultdict(Counter)
           

# file stynax uid <tab> tweets_contents
with open('open_file') as text_file:
    for index,line in enumerate(text_file): 
        split_list = line.split('t')
        if len(split_list) <2: continue
        words = wordpunct_tokenize(split_list[1])
        for n in range(2, max_distance + 2):
            ngram_counts[n].update(filter(ngram_is_valid, to_ngrams(words, n)))

skip_bigram_info = defaultdict(lambda: defaultdict(lambda: Counter()))
for n in range(2, max_distance + 2):#找出每個距離中的字典
    for key in ngram_counts[n]:#找出key
                    skip_bigram_info[key[0]][key[-1]][(n - 1)] += ngram_counts[n][key]
                    skip_bigram_info[key[-1]][key[0]][(1 - n)] += ngram_counts[n][key]

skip_bigram_abc = defaultdict(lambda:  0)
for first in skip_bigram_info:
    num_of_first = 0#第一個字後的總數量
    freq_of_first = 0#第一個字後的總值
    rms_of_first = 0#第一個字後的總軍方跟
    for second in skip_bigram_info[first]:
        freq = 0
        
        for distance in skip_bigram_info[first][second]:
            freq +=  skip_bigram_info[first][second][distance]
            
        num_of_value = 10      

        freq_of_first += freq
        
        avg = freq/num_of_value
        rms = 0
        true_rms = 0

        for distance in range(-5,6):
            if distance == 0:
                continue
            rms += (skip_bigram_info[first][second][distance]-avg)**2
            true_rms += skip_bigram_info[first][second][distance] ** 2
        
        rms_of_first += rms
        true_rms = (true_rms/num_of_value)**(0.5)
        spread = (rms/num_of_value )
 
        skip_bigram_abc[(first,second,'spread')] = spread
        skip_bigram_abc[(first,second,'freq')] = freq
        skip_bigram_abc[(first,second,'avg_freq')] = avg
        skip_bigram_abc[(first,second,'rms')] = true_rms

    avg_of_first = sum(skip_bigram_abc[(first,collocate,'freq')] for collocate in skip_bigram_info[first].keys())/len(skip_bigram_info[first])
  
    test = 0
    for collocate in skip_bigram_info[first].keys():
        test += (skip_bigram_abc[(first,collocate,'freq')]-avg_of_first)**2
    dev_of_first = (test/len(skip_bigram_info[first]))**(0.5)
    
    skip_bigram_abc[(first,'avg_freq')] = avg_of_first
    skip_bigram_abc[(first,'dev')] = dev_of_first 

# # Smadja’s 3 rule to filter skip bigrams
# 
# $$\begin{cases} 
# strength = \frac{freq - \bar{f}}{\sigma} \ge k_0 & (C_1)\\
# spread \ge u_0 & (C_2) \\
# p_j^i \ge \bar{p_i} + (k_1 \times \sqrt{u_i}) & (C_3) 
# \end{cases}$$

cc = []

base_col_freq = defaultdict(lambda:  defaultdict(lambda:  0))
for first in skip_bigram_info:
    for second in skip_bigram_info[first]:
        #C1 strength
        if skip_bigram_abc[(first,'dev')] == 0:
            break
        strength = (skip_bigram_abc[(first,second,'freq')]-skip_bigram_abc[(first,'avg_freq')])/skip_bigram_abc[(first,'dev')]
        if strength >= k0:
            #C2 spread
            spread = skip_bigram_abc[(first,second,'spread')]
            if spread >= U0:
                for distance in skip_bigram_info[first][second]:
                    #C3
                    ui = skip_bigram_abc[(first,second,'rms')]**(0.5)
                    if skip_bigram_info[first][second][distance] > skip_bigram_abc[(first,second,'avg_freq')]+(k1*ui):
                        peak = skip_bigram_abc[(first,second,'avg_freq')]+(skip_bigram_abc[(first,second,'spread')]**(0.5))
                        
                        base_col_freq[first][second] += skip_bigram_info[first][second][distance]
                        cc += [(first,second,distance,strength,spread,peak,skip_bigram_info[first][second][distance])]

dd = []

for first in base_col_freq:
    for second, freq in base_col_freq[first].iteritems():
        dd += [(first+'-'+second,int(freq))]



dd_chart = pandas.Series([freq for first in base_col_freq for second, freq in base_col_freq[first].iteritems()], 
                         index= [first+'-'+second for first in base_col_freq for second in base_col_freq[first]]).sort_values(ascending=False)
figure = dd_chart.head(100).plot(kind='bar',figsize=(20, 10))

fig = figure.get_figure()
fig.savefig('output_img_file',dpi= 300)


# ## pandas Dataframe to show the data


import pandas
collocations_df = pandas.DataFrame(cc,
                                   columns = ['base word', 'collocate', 'distance', 'strength', 'spread', 'peak', 'p'])
collocations_df = collocations_df.set_index(['base word', 'collocate', 'distance']).sort_index()


collocations_f = pandas.DataFrame(dd, columns = ['base word-collocate', 'freq'])
collocations_f = collocations_f.set_index(['base word-collocate', 'freq']).sort_index()


# ### show collocation Dataframe

collocations_f.to_csv('output_csv_file', sep=',', encoding='utf-8')
collocations_df.to_csv('output_csv_file', sep=',', encoding='utf-8')

