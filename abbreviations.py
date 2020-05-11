# imports
import spacy
from scispacy.abbreviation import AbbreviationDetector
import os
import json
import csv 

SUBSET = 'comm_use_subset_100'

# Paths
sci_md = "/mnt/c/Users/Sonja/OneDrive/Dokument/Skola/Projektkurs/en_core_sci_md-0.2.4/en_core_sci_md/en_core_sci_md-0.2.4"
comm_use_subset = "/mnt/c/Users/Sonja/OneDrive/Dokument/Skola/Projektkurs/comm_use_subset_100/"
metadata_path = "/mnt/c/Users/Sonja/OneDrive/Dokument/Skola/Projektkurs/edan70/metadata_comm_use_subset_100.csv"

# load pre trained model by spaCy
nlp = spacy.load(sci_md)
abreviation_pipe = AbbreviationDetector(nlp)
nlp.add_pipe(abreviation_pipe)

# All articles in comm_use_subset_100
all_articles = os.listdir(SUBSET)
def get_title(article):
    '''
    Returns the title of the article
    '''
    title = []
    with open(comm_use_subset + article) as file:
        f = json.load(file)
        title.append(f["metadata"]["title"])
    title = ''.join(title)
    # unsure if abbreviation part is added for the title
    return title

def get_abstract(article):
    '''
    Returns the "Abstract" of the article
    in full text (unsure if return is necessary though) 
    '''
    abstract = []
    with open(comm_use_subset + article) as file:
        f = json.load(file)
        for word in f["abstract"]:
            abstract.append(word["text"])
        
        abstract = ''.join(abstract) # convert text from list to string
        
        # Add abbreviation class in abstract with detected abbreviations
        f["abstract"][0]["abbreviations"] = get_abbreviations(abstract)
    return abstract

def get_body_text(article):
    '''
    Returns the body text of the article
    in full text (unsure if return is necessary though) and puts the abbreviations
    into the last segment of the body text part

    This should be parted for each section of the body text
    '''
    body_text = []
    with open(comm_use_subset + article) as file:
        f = json.load(file)
        for word in f["body_text"]:
            body_text.append(word["text"])
        
        body_text = ''.join(body_text) # convert text from list to string
        # Add abbreviation class in abstract with detected abbreviations
        f["body_text"][0]["abbreviations"] = get_abbreviations(body_text)
        #print(f["body_text"][0])

    return body_text

def get_abbreviations(text): 
    '''
    Returns the abbreviations used in the text in a list 
    '''
    art = nlp(text)
    abbr = art._.abbreviations
    return abbr

def get_metadata():
    metadata = {}
    with open(metadata_path, 'r') as file:
        f = csv.reader(file)
        i = 0 # skip first line
        for row in f:
            if i == 0:
                i = i+1
            else:
                metadata[row[1]] = [row[0], row[2], row[5]] # cord_uid, sourcedb (source_x in this case), sourceid (pmcid in this case)
                i = i+1
        #print(len(metadata))  # Check that all the aricles are included
    return metadata

def get_divid(text):
    '''
    FIX THIS: index nbr should not be bound to the
    specific part, if there is no abstract but only title and body_text,
    then title is 0 and body_text 1. See discord general chat.
    '''
    divid = 0
    if text == "title":
        divid = 0
    elif text == "abstract":
        divid = 1
    else:
        divid = 2
    return divid

def abbr_denotation(text):
    denotation = []
    abbreviations = get_abbreviations(text)
    for abbr in abbreviations:
        denote = {}
        denote["id"] = str(abbr)
        denote["span"] = {}
        denote["span"]["begin"] = abbr.start_char
        denote["span"]["end"] = abbr.end_char
        denote["obj"] = "Abbreviation"
        denotation.append(denote)
    return denotation




def make_pubannotation(metadata, part, text, denonation):
    '''
    Make a pubannotation from the data. NOTE: IMPLEMENT LATER PROPERLY, JUST SHELL RN
    part is part in article, text is the text in the part of the article
    '''
    pubannotation = {}
    pubannotation["cord_uid"] = str(metadata[0])
    pubannotation["source_x"] = str(metadata[1])
    pubannotation["pmcid"] = str(metadata[2])
    pubannotation["divid"] = str(get_divid(part))
    pubannotation["text"] = text
    pubannotation["project"] = "cdlai_CORD-19"
    pubannotation["denotations"] = abbr_denotation(text)
    
    return pubannotation


def main():
    article = all_articles[1] # add a loop here to do this for all articles
    title = get_title(article)
    abstract = get_abstract(article)
    body_text = get_body_text(article)
    metadata = get_metadata()
    #print("Article:", article)
    #print("metadata: ", metadata)
    sha = article[:-5] # strip article with .json format ending
    #print(sha)
    #print(metadata[sha]) # what if the article has 2 sha, will metadata[sha] look in both these if its a match? probs, but double check
    '''
    testing
    abbreviations = get_abbreviations(abstract)
    print(abstract)
    print("Abbreviations: ", abbreviations)
    print(abbr_denotation(abstract)) # WORKS
    '''
    denotation = abbr_denotation(abstract)
    pubannotation = make_pubannotation(metadata[sha], "abstract", abstract, denotation)
    print(pubannotation)

    '''
    Stuff to fill in with later when implemented
    '''
    # denotations_title = get_denotations(title)
    # denotations_abstract = get_dentations(abstract)
    # denotations_body_text = get_denotations(body_text)

    # pubannotation_title = make_pubannotation(metadata[sha], title, denotations)
    # pubannotation_abstract = make_pubannotation(metadata[sha], abstract, denotations)
    # pubannotation_body_text = make_pubannotation(metadata[sha], body_text, denotations)
    # export all pubannotations to separate files

    

if __name__ == "__main__":
    main()


