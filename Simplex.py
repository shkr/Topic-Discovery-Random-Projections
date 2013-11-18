import numpy as np
from numpy import matlib

from corpus_module import corpus

class TopicDiscovery:

    ### Function Descriptions : ##############################################
    ### 1. solve_LinearReg(Y,Theta) - solves linear regression of the form - Y = Beta*Theta, outputs : Beta         ##
    ### 2. spectral_clusters(weights,clusters) - Does spectral clustering on the given square adjacency matrix to   ##
    ### seperate given number of 'clusters'. Outputs list of labels for each node or/row number in the adjancency   ##
    ### matrix                                                                                                      ##
    ##################################################################################################################
    
    def __init__(self,verbose,NumberOfDocs=100,No_of_Topics=20):

        # Create Corpus for Topic Discovery from a relevant class 
        self.CORPUS =corpus(auto_generate=NumberOfDocs)
        self.CORPUS.create_corpus()

        # Final Number of documents in corpus stored in -> M 
        # No_Of_Topics that is passed as an input -> K
        # Typically K < M  in order for the mixed model distribution
        # distribution to hold true
        self.M = self.CORPUS.final_doc_list()
        self.K = min(No_of_Topics,self.M-1)

        #Word (Rows) Documents (Columns) Matrix
        # X[i,j] =: WordCount_in_Doc(j)(Wi) / TotalWordCount_in_Doc(j)
        self.X = self.CORPUS.ColumnNormalize()
        self.XBar=self.X/self.X.sum(axis=1)

        #Find novel words for each topic by RandomProjection method
        self.I = self.find_NovelVectors(self.XBar,self.K)
        # Find Theta matrix by spectral clustering of novel words into K clusters
        # Theta(i) = avg( X(j) for j in cluster (i) )
        self.ThetaBar = self.find_ThetaBar()

        ## Find Beta matrix by linear regression
        ## min || X~ - B~(THETA)~ ||^2
        BetaBar = self.XBar*np.linalg.pinv(self.ThetaBar)
        BetaDash = BetaBar/(1/self.X.sum(axis=1))
        self.Beta= BetaDash / BetaDash.sum(axis=0)

        #Calculate Theta matrix
        self.Theta=np.linalg.pinv(self.Beta)*self.X

    def isInvertible(self,A):
        if np.isfinite(np.linalg.cond(A)):
            return True
        else:
            return False
        
    def print_diagnostics(self):
        print "X-Matrix"
        print self.X

    #Method : Find novel words using Random projections method
    def find_NovelVectors(self,MAT,Projections):
        
        #Using random projections in unit sphere
        I=[]
        Loops = 50
        
        for vec in range(0,Loops*Projections):

           d=np.random.uniform(low=0,high=1,size=[1,self.M])
           imax = max([(np.inner(MAT[i],d),i) for i in range(0,len(MAT))])[1]
           imin = min([(np.inner(MAT[i],d),i) for i in range(0,len(MAT))])[1]
          
           I+=[imax,imin]

        return sorted(set(I))

    def find_UniqueNovelVectors(self,nodes,clusters):

        weights=[[0]*len(nodes) for i in range(len(nodes))]
        
        sigma = 0.01
        for i in range(0,len(nodes)):
            j=i+1
            while j<len(nodes):
               weights[i][j]=np.exp(float(-sigma*( (nodes[i]*nodes[i].T) - (2*nodes[i]*nodes[j].T) + (nodes[j]*nodes[j].T)) ))
               weights[j][i]=np.exp(float(-sigma*( (nodes[i]*nodes[i].T) - (2*nodes[i]*nodes[j].T) + (nodes[j]*nodes[j].T)) ))
               j=j+1            
            #for j in range(0,len(nodes)):
            #   weights[i].append(np.exp(float(-sigma*( (nodes[i]*nodes[i].T) - (2*nodes[i]*nodes[j].T) + (nodes[j]*nodes[j].T)) )))
                
        labels = self.spectral_clusters(np.matrix(weights,dtype=np.float64),clusters)
        return labels
        
    def spectral_clusters(self,weights,clusters):
        from sklearn.cluster import spectral_clustering as sc
        labels = sc(weights,clusters)
        return list(labels)

    def find_ThetaBar(self):
        Theta=[]
        nodes = [self.XBar[i] for i in self.I]
        labels = self.find_UniqueNovelVectors(nodes,self.K)
        
        set_labels = set(labels)
        for L in set_labels:
            ThetaRow=np.zeros((1,self.M))
            print "Label : " +str(L)
            for i in range(0,len(self.I)):
                if L==labels[i]:
                    print "Novel word vectors"
                    print self.XBar[self.I[i]]
                    ThetaRow = ThetaRow + np.array(self.XBar[self.I[i]])
            
            Theta.append((ThetaRow[0]/labels.count(L)).tolist())

        return np.matrix(Theta,dtype=np.float64)
    
