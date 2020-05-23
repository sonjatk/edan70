'''
Abbreviation detector based on the spaCy abbreviation detector for a subset of biomedical articles.
Developed for text mining project within the course EDAN70 Computer Science project at Lund University,
Computer Science, Faculty of Engineering.

Made by: Sonja Kenari
'''


# Imports
import spacy
from scispacy.abbreviation import AbbreviationDetector
import os
import json
import time
import csv 

SUBSET = 'comm_use_subset_100'

# Paths
sci_md = "/mnt/c/Users/Sonja/OneDrive/Dokument/Skola/Projektkurs/en_core_sci_md-0.2.4/en_core_sci_md/en_core_sci_md-0.2.4"
comm_use_subset = "/mnt/c/Users/Sonja/OneDrive/Dokument/Skola/Projektkurs/comm_use_subset_100/"
metadata_path = "/mnt/c/Users/Sonja/OneDrive/Dokument/Skola/Projektkurs/edan70/metadata_comm_use_subset_100.csv"
print("Loaded paths.")

# load pre trained model by spaCy
print("Loading pre-trained models by spaCy...")
nlp = spacy.load(sci_md)
abreviation_pipe = AbbreviationDetector(nlp)
nlp.add_pipe(abreviation_pipe)
print("Done loading. \nStarting generating pubannotation files...")


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
    return title

def get_abstract(article):
    '''
    Puts all of the sections in the abstract into a list and adds the 
    abbreviations for the section of text.
    '''
    abstract = []
    abstracts = []
    with open(comm_use_subset + article) as file:
        f = json.load(file)
        for i in range(len(f["abstract"])):
            #print(len(f["abstract"]))
            abstract = []
            #print(f["abstract"][i]["text"])
            abstract.append(f["abstract"][i]["text"])
            abstract = ''.join(abstract)
            if f["abstract"][i] != '':
                f["abstract"][i]["abbreviations"] = get_abbreviations(abstract)
            abstracts.append(abstract)
         
    return abstracts

def get_body_text(article):
    '''
    Puts all of the sections in the body text into a list and adds the 
    abbreviations for the section of text.
    '''
    body_text = []
    body_texts = []
    with open(comm_use_subset + article) as file:
        f = json.load(file)
        for i in range(len(f["body_text"])):
            body_text = []
            body_text.append(f["body_text"][i]["text"])
            body_text = ''.join(body_text)
           
            if f["body_text"][i] != '':
                f["body_text"][i]["abbreviations"] = get_abbreviations(body_text)
            body_texts.append(body_text)
       
    return body_texts

def get_abbreviations(text): 
    '''
    Returns the abbreviations detected by the spaCy abbreviation detector in the input text.
    Abbreviations are returned in a list. 
    '''
    art = nlp(text)
    abbreviations = art._.abbreviations
    
    return abbreviations

def get_metadata():
    metadata = {}
    with open(metadata_path, 'r') as file:
        f = csv.reader(file)
        i = 0 # skip first header line
        for row in f:
            if i == 0:
                i = i+1
            else:
                if '; ' in row[1]: # handle case with articles that have 2 different sha's
                    row[1] = row[1].split('; ')
                    for article in all_articles:
                        if row[1][0] == article[:-5]:
                            row[1] = row[1][0]
                        elif row[1][1] == article[:-5]:
                            row[1] = row[1][1]
                        else:
                            continue
                metadata[row[1]] = [row[0], row[2], row[5]] # cord_uid, sourcedb (source_x in this case), sourceid (pmcid in this case)
                i = i + 1
    return metadata

def abbr_denotation(text):
    denotation = []
    abbreviations = get_abbreviations(text)
    i = 1
    for abbr in abbreviations:
        denote = {}
        denote["id"] = "S-scispacy-abbr_T" + str(i)
        denote["span"] = {}
        denote["span"]["begin"] = abbr.start_char
        denote["span"]["end"] = abbr.end_char
        denote["obj"] = "Abbreviation"
        denotation.append(denote)
        i = i + 1
    return denotation

def make_pubannotation(article, metadata, part, text, divid):
    '''
    Make a pubannotation from the data. 
    article = the file name for the article
    metadata = the metadata for that article that is wanted
    part = which part of the article in a string, e.g "title"
    text = text content of the part of the article
    '''
    pubannotation = {}
    pubannotation["cord_uid"] = str(metadata[0])
    pubannotation["source_x"] = str(metadata[1])
    pubannotation["pmcid"] = str(metadata[2])
    pubannotation["divid"] = str(divid)
    pubannotation["text"] = text
    pubannotation["project"] = "cdlai_CORD-19"
    pubannotation["denotations"] = abbr_denotation(text)
    
    return pubannotation

def export_file(article, id, part, pubannotation, divid):
    '''
    Write the file for the part of the article to an output folder named "pubannotation"
    '''
    name = id + '-' + str(divid) + '-' + part
    path = "/mnt/c/Users/Sonja/OneDrive/Dokument/Skola/Projektkurs/edan70/pubannotation/" + name + '.json'
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(pubannotation, f, ensure_ascii=False, indent=4)
 
def main():
    '''
    Goes through all articles in the comm_use_subset_100 and generates pubannotation files for each part of the article.
    '''
    n = 1
    metadata = get_metadata()

    for article in all_articles:
        if article != '.DS_Store':
            print("article: ", article)
            title = get_title(article)
            print("Extracted title for ", article)
            abstracts = get_abstract(article)
            print("Extracted abstract for ", article)
            body_texts = get_body_text(article)
            print("Extracted body_text for ", article)

            denotations = []
            sha = article[:-5]
            divid = 0

            if title != '':
                pubannotation_title = make_pubannotation(article, metadata[sha], "title", title, divid)
                export_file(article, metadata[sha][0], "title", pubannotation_title, divid)
                print("Generated pubannotation file for title.")
                divid = divid + 1
            if abstracts != []:
                for i in range(len(abstracts)):
                    pubannotation_abstract = make_pubannotation(article, metadata[sha], "abstract", abstracts[i], divid)
                    export_file(article, metadata[sha][0], "abstract", pubannotation_abstract, divid)
                    print("Generated pubannotation file for abstract part nr : ", divid)
                    divid = divid + 1
            if body_texts != []:
                for i in range(len(body_texts)):
                    pubannotation_body_text = make_pubannotation(article, metadata[sha], "body_text", body_texts[i], divid)
                    export_file(article, metadata[sha][0], "body_text", pubannotation_body_text, divid)
                    print("Generated pubannotation file for body_text part nr : ", divid)
                    divid = divid + 1

            print("Done handling article: ", n, '\n\n')
            n = n+1

if __name__ == "__main__":
    main()


