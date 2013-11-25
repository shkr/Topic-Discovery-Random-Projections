#Test file


def test():
    
    from Simplex import TopicDiscovery as TD
    
    run = TD(verbose=True,NumberOfDocs=5000,No_of_Topics=30)
    import heapq
    wordlist=50
    
    print "Topic-Word distribution"
    TopicNames={}
    textk="<h2><p> Top ranking words in topics </p> </h2><h3>"
    for k in range(0,run.K):
        
        topwords = [t[0] for t in heapq.nlargest(wordlist, enumerate(run.Beta[:,k]), lambda t: t[1])]
        #topwords = [run.Beta.index(Bwk) for Bwk in sorted(run.Beta[:,k])[0:10]]
        topictext = str([run.CORPUS.Vocab[word] for word in topwords])
        print topictext
        TopicNames[k] = raw_input("Enter name for topic :")
        textk+="<p> %s : " %TopicNames[k]+ "%s </p>" % topictext
    
    topiclist=5
    text="<h1> Stories and Topic distribution : Top Five suggested topics for each story </h1> <h3>"
    for doc in range(0,run.CORPUS.final_doc_list()):
        toptopics = [(TopicNames[t[0]],str(int(run.Theta[t[0],doc]*100))+'%') for t in heapq.nlargest(topiclist, enumerate(run.Theta[:,doc]), lambda t: t[1])]

        cursor = run.CORPUS.cd.cursor()
        cursor.execute("SELECT title from node WHERE nid=%d"%run.CORPUS.DocNode[doc])
        text+="<p> %d"%doc+" <a href='http://www.campusdiaries.com/node/%s'"% str(run.CORPUS.DocNode[doc])+" > %s </a>  - "%cursor.fetchone()+" Suggested topics by priority (high2low) "+str(toptopics)+"</p>"

    text+=textk
    '''A simple program to create an html file froma given string,
    and call the default web browser to display the file.'''

    contents = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
    <html>
    <head>
      <meta content="text/html; charset=ISO-8859-1"
     http-equiv="content-type">
      <title>Automatic categorization of stories into topics</title>
    </head>
    <body>
    %s
    </body>
    </html>
    '''
    def strToFile(text, filename):
        """Write a file with the given name and the given text."""
        output = open(filename,"w")
        output.write(text)
        output.close()

    def browseLocal(webpageText, filename='StoriesandTopics.html'):
        '''Start your webbrowser on a local file containing the text
        with given filename.'''
        
        strToFile(webpageText, filename)
    
    browseLocal(contents % text)

        
if __name__=="__main__":

    import cProfile
    cProfile.run('test()','restats')
    
