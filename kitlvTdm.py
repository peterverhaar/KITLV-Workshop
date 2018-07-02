
import string
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import xml.etree.ElementTree as ET
import requests
import zipfile
import math
import os
from os.path import isfile, join , isdir
import string

lines = list()
metadata = dict()
currentBook = ''
mfw = list()
freqText = dict()


def readFile( file ):

    global lines
    global currentBook

    currentBook = file

    lines = []

    if re.search( r'\.txt$' , file ):
        try:
            text = open( file , encoding = 'utf-8' )

            for line in text:
                lines.append(line)
        except:
            print( "Cannot read " + file + " !" )


def download_corpus(url, username, password):
    """Downloads the corpus data from the given URL"""

    r = requests.get(url, auth=(username, password))

    if r.status_code == 200:
        with open("corpus.zip", 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)

    # Unzip the corpus file to the corpus directory
    with zipfile.ZipFile("corpus.zip") as corpus_zip:
        corpus_zip.extractall("corpus")


def concordance( book , searchTerm , window ):

    global lines
    global currentBook

    if book != currentBook:
        readFile(book)

    concordance = []
    regex = r"\b" + searchTerm + r"\b"

    for line in lines:
        line = line.strip()

        if re.search( regex , line , re.IGNORECASE ):
            extract = ''

            position = re.search( regex , line , re.IGNORECASE ).start()
            start = position - len( searchTerm ) - window ;
            fragmentLength = start + 2 * window  + len( searchTerm )
            if fragmentLength > len( line ):
                fragmentLength = len( line )

            if start < 0:

                whiteSpace = ''
                i = 0
                while i < abs(start):
                    whiteSpace += ' '
                    i += 1
                extract = whiteSpace + line[ 0 : fragmentLength ]
            else:
                extract = line[ start : fragmentLength ]

            print( extract )
            if re.search( '\w' , extract ) and re.search( regex , extract ):
                concordance.append( extract )
    return concordance



def removeStopwords( wordsDict ):

    mfw = []
    wordsDict2 = dict()

    try:
        mfwFile = open( 'mfw.txt' )
        for word in mfwFile:
            mfw.append( word.strip() )
    except:
        print("Cannot read the list of stopwords!")

    for w in wordsDict:
        if not( w in mfw ):
            wordsDict2[w] = wordsDict[w]

    return wordsDict2


def collocation( book , searchTerm , distance ):

    global lines
    global currentBook

    if book != currentBook:
        readFile(book)

    regex = r"\b" + searchTerm.lower() + r"\b"
    freq = dict()

    paragraph = ''

    parLength = 0

    for line in lines:
        line = line.strip()
        if parLength < 100:
            parLength += len(line)
            paragraph += line + ' '
        else:
            parLength = 0
            words = tokenise( paragraph )
            i = 0
            for w in words:
                if re.search( regex , w , re.IGNORECASE ):

                    for x in range( i - distance , i + distance ):
                        if x >= 0 and x < len(words) and searchTerm != words[x]:
                            if len(words[x]) > 0:
                                freq[ words[x] ] = freq.get( words[x] , 0 ) + 1

                i += 1
            paragraph = ''
    return freq



def collocationPos( book , searchTerm , distance, posFilter ):

    ns = {'t': 'http://www.tei-c.org/ns/1.0' }

    freq = dict()

    regex = r"\b" + searchTerm.lower() + r"\b"
    wordsDict = dict()
    index = 0

    tree = ET.parse(book)
    root = tree.getroot()

    pars = root.findall('t:text/t:p' , ns )
    for p in pars:
        sent = p.findall('t:s' , ns )
        for s in sent:
            words = s.findall('t:w' , ns )
            for w in words:
                lemma = ''
                pos = ''
                if 'lemma' in w.attrib:
                    lemma = w.attrib['lemma']
                if 'pos' in w.attrib:
                    pos = w.attrib['pos']
                if re.search( '\w' , lemma ):
                    wordsDict[index] = ( lemma, pos )
                    index += 1


    for index in wordsDict:
        if re.search( regex , wordsDict[index][0] , re.IGNORECASE ):
            for x in range( index - distance , index + distance ):
                if x >= 0 and x < len(wordsDict) and searchTerm != wordsDict[index][0]:
                    if len( wordsDict[x][0] ) > 0 and re.search( posFilter , wordsDict[x][1] , re.IGNORECASE ):
                        freq[ wordsDict[x][0].lower() ] = freq.get( wordsDict[x][0].lower() , 0 ) + 1

    return freq




def getWordsByPosTag( book , posFilter ):

    ns = {'t': 'http://www.tei-c.org/ns/1.0' }

    wordsList = dict()

    tree = ET.parse(book)
    root = tree.getroot()

    pars = root.findall('t:text/t:p' , ns )
    for p in pars:
        sent = p.findall('t:s' , ns )
        for s in sent:
            words = s.findall('t:w' , ns )
            for w in words:
                if 'pos' in w.attrib:
                    if re.search( posFilter , w.attrib['pos'] ):
                        wordsList[ w.text ] = wordsList.get( w.text , 0 ) + 1

    return wordsList




def numberOfSentences():
    #print( self.fullText )
    global fullText
    s = sent_tokenize(fullText)
    return len(s)

def tokenise( text ):
    text = text.lower()
    text = re.sub( '--' , ' -- ' , text)
    words = re.split( r'\s+' , text )
    i = 0
    for w in words:
        words[i] = w.strip( string.punctuation )
        i += 1
    return words


def fleschKincaid():
    totalWords = numberOfTokens()
    totalSentences = numberOfSentences()
    totalSyllables = numberOfSyllables()

    fk = 0.39 * (  totalWords / totalSentences )
    fk = fk + 11.8 * ( totalSyllables / totalWords )
    fk = fk - 15.59
    return fk

def sentimentAnalysis( book ):

    count = dict()
    ns = {'t': 'http://www.tei-c.org/ns/1.0' }

    wordsList = dict()

    tree = ET.parse(book)
    root = tree.getroot()

    pars = root.findall('t:text/t:p' , ns )
    for p in pars:
        sent = p.findall('t:s' , ns )
        for s in sent:
            words = s.findall('t:w' , ns )
            for w in words:

                count['all'] = count.get( 'all' , 0 ) + 1

                attr = w.attrib
                if 'ana' in w.attrib:

                    if w.attrib['ana'] == '++':
                        count['positive'] = count.get( 'positive' , 0 ) + 2

                    elif w.attrib['ana'] == '+':
                        count['positive'] = count.get( 'positive' , 0 ) + 1
                    elif w.attrib['ana'] == '-':
                        count['negative'] = count.get( 'positive' , 0 ) + 1
                    elif w.attrib['ana'] == '--':
                        count['negative'] = count.get( 'positive' , 0 ) + 2


    return count




def getPositiveWords( book ):
    return getTaggedWords( book , '++' )

def getNegativeWords( book ):
    return getTaggedWords( book , '--' )

def getTaggedWords( book , tag  ):


    wordsList = dict()

    ns = {'t': 'http://www.tei-c.org/ns/1.0' }

    tree = ET.parse(book)
    root = tree.getroot()

    pars = root.findall('t:text/t:p' , ns )
    for p in pars:
        sent = p.findall('t:s' , ns )
        for s in sent:
            words = s.findall('t:w' , ns )
            for w in words:
                if 'ana' in w.attrib:

                    if w.attrib['ana'] == tag:
                        wordsList[ w.text.lower() ] = wordsList.get( w.text.lower() , 0 ) + 1


    return sorted( wordsList )



def showTitle( book ):
    book = re.sub( '\.xml$' , '' , book )
    book = re.sub( '\.txt$' , '' , book )
    global metadata
    if len(metadata) == 0:
        md = open( 'metadata.csv' )
        for line in md:
            values = re.split( r'(?<!\\),', line )
            if re.search ( '\d' , values[0] ):
                metadata[ values[0] ] = values[3].strip()
                if re.search( '\d' , values[1] ):
                    metadata[ values[0] ] += ' ({})'.format( values[1].strip() )

    metadata[ book ] = metadata[ book ].replace('\\', " ")
    return metadata[ book ]




def countLexiconWords( book , file ):


    lexicon = open( file , encoding = 'utf-8')
    listOfWords = []

    for line in lexicon:
        line = line.strip()
        listOfWords.append(line.lower() )

    countOccurrences = 0

    ns = {'t': 'http://www.tei-c.org/ns/1.0' }

    tree = ET.parse(book)
    root = tree.getroot()

    pars = root.findall('t:text/t:p' , ns )
    for p in pars:
        sent = p.findall('t:s' , ns )
        for s in sent:
            words = s.findall('t:w' , ns )
            for w in words:
                if 'lemma' in w.attrib:
                    if w.attrib['lemma'].lower() in listOfWords:
                        countOccurrences += 1

    return countOccurrences




def calculateWordFrequencies( book ):

    global lines
    global currentBook


    if book != currentBook:
        readFile(book)


    freq = dict()

    for line in lines:
        words = tokenise( line )
        for w in words:
            if re.search( r'\w' , w ):
                if w not in mfw:
                    freq[w] = freq.get( w , 0 ) + 1

    return freq

def numberOfTypes( cap ):
    nrTypes = 0
    freq = calculateWordFrequencies( cap )
    nrTypes =  len(freq)
    return ( nrTypes )

def numberOfTokens(  book ):
    nrTokens = 0
    freq = calculateWordFrequencies(  book )
    for w in freq:
        nrTokens += freq[w]
    return ( nrTokens )

def tdIdf( corpus , book ):

    global freqText
    book = os.path.basename( book )

    freq = dict()


    txt = []

    ## Formula is as follows: tf-idf= log⁡(⁡ N /df ),
    # tf being the number of times a term appears in a document,
    # N being the total number of documents
    # df being the number of documents in which the term appears.

    if len( freqText ) == 0:

        fnames = os.listdir( corpus )
        for i in fnames:
            if re.search( '[.]txt$' , i):
                txt.append( i )

        ## N is total number of texts
        N = len(txt)

        for t in txt:
            textWords = []
            text = open( join( corpus , t ) , encoding = 'utf-8' )

            for line in text:
                words = tokenise( line )
                for w in words:
                    freq[w] = freq.get( w , 0 ) + 1
                    freqText[ (t , w ) ] = freq.get( (t , w ) , 0 ) + 1


        idf = dict()
        ## df is number of texts in which the term appears

        for word in freq:
            df = 0

            for text in txt:
                if ( text , word ) in freqText:
                    df += 1

            idfW = math.log( N / df )
            idf[ word ] = idfW

            for text in txt:
                if ( text , word ) in freqText:
                    freqText[ ( text , word ) ] = 1 + freqText[ ( text , word ) ] * idf[ word ]

        print( 'Done: Calculations made.' )


    freqIdf = dict()
    allWords = dict()

    for w in freqText:
        print(freqText[w][1])
        allWords.appen( freqText[w][1] )

    for w in allWords:
        if( book , w ) in freqText:
            freqIdf[w] = freqText[ ( book , w ) ]
            i += 1
            if i == max:
                break

    return freqIdf



def countPosTag( posRe ):
    global posTags

    countTags = 0

    for tag in posTags:
        if re.search( posRe , tag ):
            countTags += posTags[tag]
    return countTags
