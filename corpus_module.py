import MySQLdb

import re
import numpy as np
import nltk

from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class corpus:


    #corpus.__doc__= "This class contains all associated data points and methods associated with the word-document distribution matrix (A)"
    init_list_of_nid = [1354,1358,1360,1368,1373]
    #Corpus : Amatrix - Word document distribution matrix
    DocList=[]
    Amat=[]

    #Vocabulary
    Vocab = []

    #Default list of documents
    init_list_of_nid = [1354,1358,1360,1368,1373]
    
    def __init__(self,auto_generate):
        
        #Make connection to database
        self.cd = MySQLdb.connect(host="localhost", user = "root", db = "campus031013")

        self.limit=auto_generate
        self.list_of_nid = self.generate_nodelist()
        self.min_docsize = 100
        self.DocNode=[]
        
        
    def generate_nodelist(self):
        cursor = self.cd.cursor()
        cursor.execute("SELECT nid from node WHERE type='normal_story' AND uid>1")
        list_nids = [ int(nid[0]) for nid in cursor.fetchall()]
        cursor.close()
        print "List of nids considered : "+str(list_nids[0:self.limit])
        return list_nids[0:self.limit]
    
    def process_data(self,body):

        removed_html=strip_tags(body)

        str_stop_words=open("stop_words.txt").read()
        list_stop_words = str_stop_words.split('\n')
        p_body= [x.lower() for x in re.split('\W+',removed_html) if (x and len(x)>2 and (not x.lower() in list_stop_words))]

        return p_body
    
    def create_corpus(self):

        from collections import defaultdict
        
        cursor_1 = self.cd.cursor()
        #create_corpus.__doc__="This function creates the corpus using the initialization nids"

        for i in self.list_of_nid:
            cursor_1.execute("SELECT body_value from field_data_body WHERE entity_id='%s'"%str(i))
            doc=self.process_data(str(cursor_1.fetchone()))

            #Update DocList
            if len(doc)>self.min_docsize:
                self.DocNode.append(i)
                self.DocList.append(doc)
                #Update vocabulary
                for word in set(doc):
                    if not word in self.Vocab:
                        self.Vocab.append(word)


        #Update X - matrix word-document frequency distribution matrix
        self.update_Amat()
        
    def final_doc_list(self):
        return len(self.DocList)

    
    def update_Amat(self):

        for doc in range(0,len(self.DocList)):
            Acol=[]
            for i in range(0,len(self.Vocab)):
                Acol.append(int(self.DocList[doc].count(self.Vocab[i])))

            self.Amat.append(Acol)

    def ColumnNormalize(self):
        
        X_np = np.matrix(self.Amat, dtype=np.float64).transpose()
        
        return X_np/X_np.sum(axis=0)
