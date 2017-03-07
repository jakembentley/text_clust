from nltk import word_tokenize
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import re
from nltk.stem.porter import PorterStemmer
from nltk import word_tokenize
from string import punctuation
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import Normalizer
from sklearn import metrics
from csv import DictReader
import pickle


#subset the documents so that only near-duplicates are loaded into this script:

def subset_corpus(path):
    doclist = []
    with open(path, 'r') as f:
        for line in f:
            doc = line.replace("\n", "")
            doclist.append(doc)

    return doclist
#iterate through the directory and append the file to the list


######################################
#this circumstance applies to a file dir with txt files
def corpus_from_dir(corpus_root, encoding = "utf-8"):
    corpus = []
    filelist = os.listdir(corpus_root)
    for file in filelist:
        # open the file
        with open(corpus_root +"/" + file, 'r', encoding = encoding) as f:
            doc = f.read().replace('\n', '')
            doc = doc.lower()
            corpus.append(doc)
    return corpus
#######################################

#######################################
#this circumstance applies to a csv file
def corpus_from_csv(corpus_root, textCol, subset = False,subsetCol= None, subsetter= None,encoding = "utf-8"):
    corpus = []
    with open(corpus_root, 'r', encoding = encoding) as f:
        reader = DictReader(f)
        data = [row for row in reader]

    #this should eliminate uninteresting documents

    for row in data:
        if subset == True:
            key = row[subsetCol]
            if key not in subset:
                continue

        content = row[textCol]
        corpus.append(content)

    return corpus
#######################################

#some post corpus text preprocessing
def preprocess_doc(corpus, stemmer):
    '''
    preprocesses a corpus here implemented as a list of strings
    to remove lowercase, stem, remove numbers and punctuation
    '''
    corpus =[[stemmer.stem(word) for word in doc.split(" ") if word not in punctuation] for doc in corpus]
    corpus =[[word.lower() for word in doc] for doc in corpus]
    corpus =[' '.join(item) for item in corpus]
    corpus =[re.sub('\d', '', item) for item in corpus]
    corpus =[re.sub('[.,()]', '', item) for item in corpus]

    return corpus
def vectorize(corpus, tfidf = True, lsa = True, nfeatures = 100):
    '''
    vectorizes documents in a corpus
    by default implements tfidf normalization

    returns a sparse matrix X
    '''
    lsi = None
    vect = CountVectorizer(input = 'content', stop_words='english', encoding = 'latin-1')
    tfxidf = TfidfTransformer(norm = 'l2', smooth_idf = True)

    X = vect.fit_transform(corpus)
    if tfidf == True:
        X = tfxidf.fit_transform(X)
    if lsa == True:
        svd = TruncatedSVD(nfeatures)
        normalizer = Normalizer(copy = False)
        lsi = Pipeline(steps = [('svd', svd), ('normalizer', normalizer)])
        X = lsi.fit_transform(X)

    return X, vect, lsi

#get tfidf weighted matrix


#preform k means clustering
#determine a good number of clusters for this particular corpus
def get_kmeans(k, X, v, pipeline, pipe = True):
    km = KMeans(n_clusters=k, init='k-means++', max_iter=100, n_init=1,
                verbose=True)
    km.fit(X)
    sil=metrics.silhouette_score(X, km.labels_, sample_size=1000)
    print("The Silhoutte Score: {}" .format(sil))

    if pipe == True:
        original_space_centroids = pipeline.named_steps['svd'].inverse_transform(km.cluster_centers_)
        order_centroids = original_space_centroids.argsort()[:, ::-1]
    else:
        order_centroids = km.cluster_centers_.argsort()[:, ::-1]

    terms = v.get_feature_names()
    for i in range(k):
        print("Cluster %d:" % i, end='')
        for ind in order_centroids[i, :10]:
            print(' %s' % terms[ind], end='')
            print()

    return km
