import numpy as np
import h5py, ast

class DeepIEP(object):
    def __init__(self, cyscam=False, modelname="Models/default", load = True):
        from keras import backend as K
        K.set_learning_phase(0)
        self.K = K

        from keras.models import load_model
        self.k_load_model = load_model
        
        self.cyscam = cyscam
        self.modelname = modelname
        if load:
            self.load()
            
    def load(self, modelname=None):        
        if type(modelname) == type(None):
            modelname = self.modelname
        self.model = self.k_load_model(modelname + ".h5")
        
        f = h5py.File(modelname + ".h5","r")
        c2i_str = f["char2idx"].value
        self.char2idx = ast.literal_eval(c2i_str)
        f.close()
        
        self.max_length = self.model.layers[0].input_shape[1]-1   
    
    def predict(self, seq):
        if type(seq) == str:
            #print "string"
            return self.predict_seq(seq)
        else:
            #print "list like"
            return self.predict_list(seq)

    def predict_seq(self, seq):
        if self.cyscam:
            seq = seq.replace("C","Z")
        vec = np.array([self.vectorize_seq(seq)])
        vec = np.flip(vec, axis=1)
        return self.model.predict(vec)[0][0]

    def predict_list(self, a):
        v = []
        for s in a:
            if self.cyscam:
                s = s.replace("C","Z")
            v.append(self.vectorize_seq(s))
        v = np.flip(v, axis=1)
        return self.model.predict(v)
                
    def vectorize_seq(self, seq):
        vec = np.zeros((self.max_length+1, len(self.char2idx.keys())+1))
        for i,char in enumerate(seq):
            j = self.char2idx[char]
            vec[i,j] = 1
        vec[len(seq):, -1] = 1
        return vec
    
    
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='DeepIEP: Prediction of isoelectric point (pI/IEP) using recurrent neural networks(RNNs)')
    parser.add_argument('--sequence','-s', nargs='*', help='An uppercase amino acid sequence to predict (Z= cyscam modified C, X=unknown')
    parser.add_argument('--file','-f', help='A CSV file with sequences to predict. Sequences must be in a column named "Sequences"')
    parser.add_argument('--full_precision', action='store_true', help='If full precision should be used when writing a CSV file')


    args = parser.parse_args()
    
    if args.sequence or args.file:
        deepiep = DeepIEP()
        if args.sequence:
            print
            for s in args.sequence:
                print s, "%0.1F"%deepiep.predict(s)
        if args.file:
            import pandas as pd
            data = pd.read_csv(args.file)
            data["DeepIEP"] = deepiep.predict_list(data["Sequences"])
            if not args.full_precision:
                data.to_csv(args.file, float_format='%.1f', index=False)
            else:
                data.to_csv(args.file, index=False)
    else:
        print "-h for usage"
       
    

    
                