
import string
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import xml.etree.ElementTree as ET

lines = list()
metadata = dict()
currentBook = ''
mfw = list()


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



def concordance( book , searchTerm , window ):

    global lines
    global currentBook

    if book != currentBook:
        readFile(book)

    concordance = []
    regex = r"\b" + searchTerm + r"\b"

    for line in lines:
        line = line.strip()
        #print( line )
        if re.search( regex , line , re.IGNORECASE ):
            extract = ''
            #print(line + '/n' )
            position = re.search( regex , line , re.IGNORECASE ).start()
            #print( position )
            start = position - len( searchTerm ) - window ;
            fragmentLength = start + 2 * window  + len( searchTerm )
            if fragmentLength > len( line ):
                fragmentLength = len( line )
            #print( start )
            #print( fragmentLength )

            if start < 0:

                whiteSpace = ''
                i = 0
                while i < abs(start):
                    whiteSpace += ' '
                    i += 1
                extract = whiteSpace + line[ 0 : fragmentLength ]
            else:
                #extract = line
                extract = line[ start : fragmentLength ]

            print( extract )
            if re.search( '\w' , extract ) and re.search( regex , extract ):
                concordance.append( extract )
    return concordance



def collocationAnalysis( book , searchTerm , distance ):

    global lines
    global currentBook
    global mfw

    if len(mfw) == 0:
        try:
            mfwFile = open( 'mfw.txt' )
            for word in mfwFile:
                mfw.append( word.strip() )
        except:
            print("Cannot read the list of stopwords!")

    if book != currentBook:
        readFile(book)

    regex = r"\b" + searchTerm.lower() + r"\b"
    freq = dict()

    paragraph = ''

    for line in lines:
        line = line.strip()
        if re.search( '\w' , line):
            paragraph += line + ' '
        else:
            words = tokenise( paragraph )
            i = 0
            for w in words:
                if re.search( regex , w , re.IGNORECASE ):
                    for x in range( i - distance , i + distance ):
                        if x >= 0 and x < len(words) and searchTerm != words[x]:
                            if len(words[x]) > 0 and words[x] not in mfw:
                                freq[ words[x] ] = freq.get( words[x] , 0 ) + 1

            i += 1
            paragraph = ''
    return freq



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
    tree = ET.parse(book)
    root = tree.getroot()

    for elem in root:
        for subelem in elem:
            count['all'] = count.get( 'all' , 0 ) + 1
            #print(subelem.text)
            attr = subelem.attrib
            '''
            if 'lemma' in subelem.attrib:
                print( subelem.attrib['lemma'] )
            if 'pos' in subelem.attrib:
                print( subelem.attrib['pos'] )
            '''

            if 'ana' in subelem.attrib:


                if subelem.attrib['ana'] == '++':
                    count['positive'] = count.get( 'positive' , 0 ) + 2
                    print( subelem.text )
                elif subelem.attrib['ana'] == '+':
                    count['positive'] = count.get( 'positive' , 0 ) + 1
                elif subelem.attrib['ana'] == '-':
                    count['negative'] = count.get( 'positive' , 0 ) + 1
                elif subelem.attrib['ana'] == '--':
                    count['negative'] = count.get( 'positive' , 0 ) + 2

                    #print( subelem.attrib['ana'] )


    '''
    par = root.findall('p'  )


    for word in par:
        print( word.find('w' ).text )
    '''
    return count




def showTitle( book ):
    global metadata
    if len(metadata) == 0:
        md = open( 'metadata.csv' )
        for line in md:
            values = re.split( r'(?<!\\),', line )
            if re.search ( '\d' , values[0] ):
                metadata[ values[0] ] = values[3].strip()
                if re.search( '\d' , values[1] ):
                    metadata[ values[0] ] += ' ({})'.format( values[1].strip() )

    if re.search( '[.]txt$' , book ):
        book = re.sub( '[.]txt$' , '' , book  )

    metadata[ book ] = re.sub( r'[\],' , ',' , metadata[ book ] )

    return metadata[ book ]






def countOccurrencesWords( listOfWords ):

    freq = dict()
    lowerCaseList = []

    for item in listOfWords:
        freq[item] = 0
        lowerCaseList.append( item.lower() )



    for line in lines:
        words = tokenise( line )
        for w in words:
            if w.lower() in lowerCaseList:
                freq[ w.lower() ] = freq.get( w.lower() , 0 ) + 1

    wordFreq = []
    for w in listOfWords:
        if w.lower() in freq:
            wordFreq.append( freq[w.lower()] )
        else:
            wordFreq.append(0)

    return wordFreq


def calculateWordFrequencies( book ):

    global lines
    global currentBook
    global mfw

    if len(mfw) == 0:
        try:
            mfwFile = open( 'mfw.txt' )
            for word in mfwFile:
                mfw.append( word.strip() )
        except:
            print("Cannot read the list of stopwords!")

    if book != currentBook:
        readFile(book)

    tokens = 0
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

def numberOfTokens():
    nrTokens = 0
    freq = calculateWordFrequencies( 0 )
    for w in freq:
        nrTokens += freq[w]
    return ( nrTokens )

def numberOfSyllables():
    nrSyllables = 0
    freq = calculateWordFrequencies( 0 )
    for w in freq:
        nrSyllables += countSyllables(w) * freq[w]
    return ( nrSyllables )

def countSyllables( word ):
    pattern = "e?[aiouy]+e*|e(?!d$|ly).|[td]ed|le\$|ble$"
    syllables = re.findall( pattern , word )
    return len(syllables)

def countPosTag( posRe ):
    global posTags

    countTags = 0

    for tag in posTags:
        if re.search( posRe , tag ):
            countTags += posTags[tag]
    return countTags
