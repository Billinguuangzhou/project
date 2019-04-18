import sys
import sif_src.data_io as data_io 
import sif_src.params as params 
import sif_src.SIF_embedding as SIF_embedding 

class SIF:

    wordfile = 'auxiliary_data/glove.840B.300d.txt' # word vector file, can be downloaded from GloVe website
    #wordfile = '../data/data_example.txt' # word vector file, can be downloaded from GloVe website
    weightfile = 'auxiliary_data/enwiki_vocab_example.txt' # each line is a word and its frequency
    weightpara = 1e-3 # the parameter in the SIF weighting scheme, usually in the range [3e-5, 3e-3]
    rmpc = 1 # number of principal components to remove in SIF weighting scheme
    words = None
    We = None
    word2weight = None
    weight4ind = None

    def __init__(self):
        # load word vectors
        (self.words, self.We) = data_io.getWordmap(self.wordfile)
        # load word weights
        self.word2weight = data_io.getWordWeight(self.weightfile, self.weightpara) # word2weight['str'] is the weight for the word 'str'
        self.weight4ind = data_io.getWeight(self.words, self.word2weight) # weight4ind[i] is the weight for the i-th word

    def calSIF(self, sen1, sen2):
        sentences = []
        sentences.append(sen1)
        sentences.append(sen2)
        # load sentences
        x, m  = data_io.sentences2idx(sentences, self.words) # x is the array of word indices, m is the binary mask indicating whether there is a word in that location
        w = data_io.seq2weight(x, m, self.weight4ind) # get word weights
        # set parameters
        params = params.params()
        params.rmpc = rmpc
        # get SIF embedding
        embedding = SIF_embedding.SIF_embedding(We, x, w, params) # embedding[i,:] is the embedding for sentence i
        if embedding.shape[0] == 2:
            sqrtVec0 = norm(embedding[0])
            sqrtVec1 = norm(embedding[1])
            product = sqrtVec0 * sqrtVec1
            if fabs(product) < 1e-6:
                return 0.
            return np.dot(vectors[0], vectors[1]) / product
        else:
            return 0.
