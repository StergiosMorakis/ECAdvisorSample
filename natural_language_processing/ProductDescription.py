# -*- coding: utf-8 -*-
from sklearn.metrics import pairwise_distances
from greeklish.converter import Converter
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer
from html.parser import HTMLParser
import unicodedata
import re
from greek_stemmer import GreekStemmer
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import nltk
import logging
from datetime import datetime
"""
Created on Thu Jan  3 11:54:10 2019

@author: stergios
"""

# Import Libraries
import numpy as np
import pandas as pd
import os
import sys
# SQL Related
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from Methods.QueryReader import *
from Methods.CleanUp import *
sys.path.remove(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# Datetime
from datetime import datetime

# Logger
import logging
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename='output'+ datetime.now().strftime('%Y%m%d%H%M%S')+'.log', level=logging.DEBUG, datefmt='%m/%d %I:%M:%S %p')
# create logger
logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)

def Initialize(varDB):
    output('Initialize')
    executeQuery('../Initializers/Update Category_Tree.sql', varDB)
    executeQuery('../Initializers/Update Product_Category_Mapping.sql',varDB)
    executeQuery('../Initializers/Update Product_Category_Mapping_Desc.sql',varDB)
    executeQuery('../Initializers/Update Product_Group_Mapping.sql',varDB)
    executeQuery('../Initializers/Unique_Group_Combination.sql', varDB)
    executeQuery('../Initializers/Product_Specs_Mapping.sql', varDB)


def output(*s):
    for prnt in s:
        logger.info(myconverter.convert(prnt))

# Import Data Preprocessing Related Libraries
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from greek_stemmer  import GreekStemmer
import re
import unicodedata
from greeklish.converter import Converter 
myconverter = Converter(max_expansions=1)

# Remove HTML Tags
from html.parser import HTMLParser
class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

# Remove Accents
def strip_accents(s):
    s = str(s)
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')

# Similar English Chars to Greek Chars Dict
def toGreekLetter(c):
    return {
        'A': 'Α',
        'B': 'Β',
        'C': 'Γ',
        'D': 'Δ',
        'E': 'Ε',
        'F': 'Φ',
        'G': 'Φ',
        'H': 'Η',
        'I': 'Ι',
        'J': 'Ξ',
        'K': 'Κ',
        'L': 'Λ',
        'M': 'Μ',
        'N': 'Ν',
        'O': 'Ο',
        'P': 'Ρ',
        'Q': 'Ξ',
        'R': 'Ρ',
        'S': 'Σ',
        'T': 'Τ',
        'U': 'Υ',
        'V': 'Ν',
        'W': 'Ω',
        'X': 'Χ',
        'Y': 'Υ',
        'Z': 'Ζ',
    }.get(c, c)

# Fix Greek Word containing English Char(s)
def toGreekWords(s):
    return ''.join(toGreekLetter(c) for c in s)

# Similar English Chars to Greek Chars Dict
def toEnglishLetter(c):
    return {
        'Α': 'A',
        'Β': 'B',
        'Γ': 'G',
        'Δ': 'D',
        'Ε': 'E',
        'Ζ': 'Z',
        'Η': 'H',
        'Θ΄': 'U',
        'Ι': 'I',
        'Κ': 'K',
        'Λ': 'L',
        'Μ': 'M',
        'Ν': 'N',
        'Ξ': 'J',
        'Ο': 'O',
        'Π': 'P',
        'Ρ': 'P',
        'Σ': 'S',
        'Τ': 'T',
        'Υ': 'Y',
        'Φ': 'F',
        'Χ': 'X',
        'Ψ': 'C',
        'Ω': 'V',
    }.get(c, c)

# Fix Greek Word containing English Char(s)
def toEnglishWords(s):
    return ''.join(toEnglishLetter(c) for c in s)

# Get English, Greek(UpperCase) StopWords
englishstopwords = set(stopwords.words('english'))
greekstopwords = [strip_accents(word.upper()) for  word in set(stopwords.words('greek'))]
# Get more StopWords like colors etc.
with open('extrastopwords.txt', encoding="utf8") as f:
    extrastopwords = [line.strip() for line in f if not line.startswith('#')]

# Stem Important English, Greek Words.
def Stemming(s):
    # Turn to UpperCase + Remove Accents
    s = strip_accents(s.upper())
    # Find Enlighs Letters in Greek Words
    listToReplace = re.findall (r'\b([Α-Ω]+[A-Z]+[Α-Ω]*|[Α-Ω]*[A-Z]+[Α-Ω]+)+\b', s)
    for word in listToReplace:
        s = s.replace(word, toGreekWords(word))
    # Find Greek Letters in English Words
    listToReplace = re.findall (r'\b([A-Z]+[Α-Ω]+[A-Z]*|[A-Z]*[Α-Ω]+[A-Z]+)+\b', s)
    for word in listToReplace:
        s = s.replace(word, toGreekWords(word))
    # For each nonStopWords Word: Stem Word + Join them all together
    s = re.sub('[^A-ZΑ-Ω]', ' ', s).split()
    ps = PorterStemmer()
    gs = GreekStemmer()
    s = ' '.join([gs.stem(ps.stem(word.lower()).upper()) for word in s if not word in greekstopwords and not word.lower() in englishstopwords and not word.lower() in extrastopwords and len(word)>2]).lower()
    return s

# Create Clean Indexed Corpus
def getStemmedDF(varDB, ignore_manufacturers):
    # Import Data
    df = getTable('ImportData/nlp_data.sql', varDB)
    # Add new Columns
    df['Corpus'] = ''
    df['FullCorpus'] = ''
    output("Start Stemming")
    if ignore_manufacturers == True:
        new_corpus_name = 'name_without_manufacturer'
        df[new_corpus_name] = df['name']
        # Import Manufacturer Names
        manufacturers = getTable('ImportData/getManufacturers.sql', varDB)
        for manufacturer in manufacturers['ManufacturerName']:
            df[new_corpus_name] = df[new_corpus_name].apply(lambda o : o.lower().replace(manufacturer.lower(), ''))
    else:
        new_corpus_name = 'name'
    # Create Corpus
    RowsToBeRemoved = []
    for i in range(0, df.shape[0]):
        name_stems = Stemming(df[new_corpus_name][i]).strip()
        short_description_stems = Stemming(df['shortDescription'][i]).strip()
        full_description_stems = Stemming(strip_tags(df['fullDescription'][i])).strip()
        category_stems = re.sub('[^a-z0-9]', ' ', df['Categories'][i].lower()).strip()
        manufacturer_stems = re.sub('[^a-z0-9]', ' ', df['Manufacturers'][i].lower()).strip()
        tagg_stems = re.sub('[^a-z0-9]', ' ', df['Taggs'][i].lower()).strip()
        specs_stems = re.sub('[^a-z0-9]', ' ', df['specs'][i].lower()).strip()
        # Combine Lists + manufacturer_stems + ' '
        corpus_data = name_stems + ' ' + category_stems + ' ' + tagg_stems
        if ignore_manufacturers == False:
            corpus_data += ' ' + manufacturer_stems
        detailed_corpus_data = corpus_data + ' ' + short_description_stems + ' ' + full_description_stems  + ' ' + specs_stems             
        if corpus_data and not corpus_data.isspace():
            df.loc[i, 'Corpus'] = corpus_data
            df.loc[i, 'FullCorpus'] = detailed_corpus_data
        else:
            RowsToBeRemoved.append(i)
    df = df.drop(RowsToBeRemoved).reset_index(drop=True)
    output("Eo Stemming")
    return df

def updateN(size):
    if size > 49:
        N = 8
    elif size > 21:
        N = 4
    else:
        N = 2
    return N

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans
def runKmeansClustering(df, cluster_size_calc = (lambda x: 8), limit_clustersize = 7, UseDetailCorpus_Limit = 40, mininertia = 0):
    df['Cluster'] = '1'
    df['ContinueClustering'] = 1
    df['Inertia'] = -0.1
    df['Features'] = 0
    output('Now Clustering ' + str(df.shape[0]) + ' EoClustering when every Cluster has less than ' + str(limit_clustersize) + ' Items')
    # Filter Clusters that should divide in smaller Clusters
    df_filtered = df.loc[df['ContinueClustering'] == 1]
    while df_filtered.groupby(['Cluster'])['Cluster'].count().max() > limit_clustersize:
        output('====================')
        # Get most frequent Cluster from the filtered ones
        sub_df=df_filtered.loc[df_filtered['Cluster']==df_filtered['Cluster'].value_counts().idxmax()].copy()
        if (sub_df.shape[0] > UseDetailCorpus_Limit):
            corpusColumnName = 'Corpus'
        else:
            corpusColumnName = 'FullCorpus'
        output('Cluster: ' + str(sub_df.loc[sub_df.index[0],'Cluster']) + ' Size: ' + str(sub_df.shape[0]))
        # Bag of Words
        cv = CountVectorizer(max_features=400)
        bow = cv.fit_transform(list(sub_df[corpusColumnName])).toarray()
        words = cv.get_feature_names()
        continue_clustering = True
        #N = N_Clusters
        N = cluster_size_calc(sub_df.shape[0])
        while N > 1:
            # Kmeans Clustering
            km = KMeans(n_clusters=int(N), init='k-means++')
            clusters = km.fit(bow)
            sub_df['newCluster'] = clusters.labels_
            sub_df['newCluster'] = sub_df['newCluster'].astype(str)
            #min_clustersize = sub_df.groupby(['newCluster'])['newCluster'].count().min()
            # if min_clustersize<=1:
            if (clusters.inertia_ <= mininertia):
                N = 1
                continue_clustering = False
                output('Inertia is Zero')
            elif (np.sum((sub_df.groupby(['newCluster']).count() == 1).reset_index(drop=True)).values[0]) >= (sub_df.groupby(['newCluster']).count()['Cluster'].count()*0.5):
                N -= 1
                continue_clustering = False
                output('Too many Clusters containing 1 item have been found! ' + str(N) + 'Clusters and continue_clustering = False' )
            else:
                break
        output('Eo Clustering on Cluster ' + sub_df.loc[sub_df.index[0],'Cluster'] + ' Inertia: ' + str(clusters.inertia_) + '  Items: '+str(sub_df.shape[0]) + ' Features: ' + str(len(words)))
        if continue_clustering == True:
            sub_df['Cluster'] += sub_df['newCluster']
            sub_df['Inertia'] = clusters.inertia_
            sub_df['Features'] = len(words)
            output('Case1 -- continue_clustering == True -- CHANGE: UPDATE CLUSTER')
        elif N == 1:
            sub_df['ContinueClustering'] = 0
            output('Case2 -- continue_clustering == False AND N==1 -- CHANGE: ContinueClustering=0')
            # To Do in the Future
            #output('Outlier Cluster: '+str(sub_df.loc[sub_df.groupby(sub_df['newCluster']).productId.count().idxmin()]))
        else:
            sub_df['Cluster'] += sub_df['newCluster']
            sub_df['Inertia'] = clusters.inertia_
            sub_df['Features'] = len(words)
            output('Case3 -- continue_clustering == True AND N!=1 -- CHANGE: UPDATE CLUSTER')
        # Update main DataFrame
        df.update(sub_df)
        df['productId'] = df['productId'].astype(int)
        # Update filter
        df_filtered = df.loc[df['ContinueClustering'] == 1]
        # Visualizing new Clusters
        Clusters = sub_df['Cluster'].unique()
        output('New Clusters:')
        order_centroids = clusters.cluster_centers_.argsort()[:, ::-1]
        for i in range(len(Clusters)):
            output('------------')
            output('Cluster: ' + Clusters[i] + ' Size: ' + str(sub_df['Cluster'][sub_df['Cluster']==Clusters[i]].count()))
            output('Most Used Words: ')
            for ind in order_centroids[i, :8]:
                output(str(ind)+' : '+(words[ind]))
        output('====================')
        # End While Loop
    return df

from sklearn.metrics import pairwise_distances
def getNearCluster(df):
    isordered, ispublished = df.copy(), df.copy()
    isordered = isordered.groupby('Cluster')['ordered'].sum()
    ispublished = ispublished.groupby('Cluster')['published'].sum()
    df_altered = pd.DataFrame()
    df_altered['Corpus'], df_altered['Cluster'] = df['Corpus'].copy(), df['Cluster'].copy()
    cv = CountVectorizer()
    bow = cv.fit_transform(list(df_altered['Corpus'])).toarray()
    bow_df = pd.DataFrame(data=bow, columns=cv.get_feature_names())
    df_altered=pd.DataFrame(data = pairwise_distances(bow_df, metric='cosine'), index = df_altered.iloc[:, -1], columns = df_altered.iloc[:, -1])
    df_altered=df_altered.groupby(df_altered.index).mean().groupby(df_altered.columns, axis = 1).mean()
    for i in range(df_altered.shape[0]):
        for j in range(df_altered.shape[1]):
            if i == j or isordered[i] + isordered[j] == 0 or ispublished[i] + ispublished[j] == 0:
                df_altered.iat[i, j] = 2
    df_altered['nearCluster'] = df_altered.idxmin(axis=1)
    df_altered['Distance'] = df_altered.min(axis=1)
    df=df.merge(df_altered.iloc[:,-2:], left_on='Cluster', right_on=df_altered.index)
    return df

# MAIN PHASE
def mainFunc(varName, varignore_manufacturers, limit_clustersize = 7):
    try:
        # Variables
        varKmeans = True
        varExportCsv = True
        varExportSql = True
        varDB = getConnectionString(varName, 1)
        # Start
        output("*********  START "+varName+" START  **********")
        output('DataBase: ' + varDB)
        # Run Initialize Queries
        if not checkTablesExist('../Initializers/checkTablesExist.sql', varDB):
            Initialize(varDB)
        # Get Stemmed DataFrame
        stemmed_df = getStemmedDF(varDB, varignore_manufacturers)
        if varKmeans:
            # Run Kmeans
            kmeans_result_df = runKmeansClustering(stemmed_df, updateN, limit_clustersize)
            # Turn Cluster XXX to cXXX
            kmeans_result_df['Cluster'] = kmeans_result_df['Cluster'].apply(lambda x : 'c' + x)
        try:
            kmeans_result_df = getNearCluster(kmeans_result_df)
        except:
            output('An error occured on getNearCluster function')
        # Export Kmeans result to sql
        if varignore_manufacturers:
            export_extension = 'withoutManufacturer'
        else:
            export_extension = 'withManufacturer'
        if varExportSql:
                ExportToSql(varDB, 'Kmeans_' + export_extension + '_Clustering', kmeans_result_df)
        # Export Kmeans result to csv
        if varExportCsv:
            if varignore_manufacturers == True:
                kmeans_result_df=kmeans_result_df.drop(columns=['name_without_manufacturer'])
                kmeans_result_df=kmeans_result_df.drop(columns=['name', 'shortDescription', 'fullDescription', 'ContinueClustering'])
                csv = datetime.now().strftime("%b%d h%Hm%M") + ' ' + varName + ' ' + export_extension + ' Clustering Results.csv'
                kmeans_result_df.to_csv('Exported/'+csv, sep='\t', encoding='utf-8-sig')
        logging.shutdown()
        output(' ------------------------------------------------------- ')
        output('Created ' + str(len(kmeans_result_df['Cluster'].unique())) + ' Clusters')
        output("*********  END "+varName+" END  **********")
        output(' ------------------------------------------------------- ')
    except Exception as e:
        output(e)

mainFunc('dbName', True)

###################################

###################################

###################################

## Birch Clustering
#from sklearn.cluster import Birch

## Search Machine
# def searchWord(s):
#    for i in range(0, N_Clusters):
#        print('Cluster',i,'having',kmeans.loc[kmeans['Cluster'] == i].count(),'items: Found word [',s,'] a total of',(kmeans[kmeans['Corpus'].str.contains(s)])['Cluster'].loc[kmeans['Cluster'] == i].count(),' times.')
##searchWord(s)

## Creating the Bag of Words model
#from sklearn.feature_extraction.text import CountVectorizer
#cv = CountVectorizer(max_features=200)
#X1 = cv.fit_transform(corpus1).toarray()
#print("[ Time ]",datetime.now().time(), "Eo CountVectorizer")
# words=cv.get_feature_names()

## Check WCSS
#from sklearn.cluster import KMeans
#import matplotlib.pyplot as plt
#wcss = []
# for i in range(0, 21):
#    kmeans = KMeans(n_clusters = i, init = 'k-means++', random_state = 42)
#    kmeans.fit(X)
#    wcss.append(kmeans.inertia_)
#plt.plot(range(1, len(wcss)+1), wcss)
#plt.title('The Elbow Method')
#plt.xlabel('Number of clusters')
# plt.ylabel('WCSS')
# plt.show()

