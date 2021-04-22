import os
import csv
import json
import PubAnnotationGenerator
from matplotlib import pyplot as plt 
import numpy as np  
import pickle

SUBSET = 'comm_use_subset_100'
all_articles = os.listdir(SUBSET)

scrape_path_abbr = './data/scrape_abbr/'
spacy_path = './edan70/pubannotation/'
spacy_path_abbr = './data/spacy_abbr/'
metadata_path = "./metadata_comm_use_subset_100.csv"


scrape_abbrv = os.listdir(scrape_path_abbr)
spacy_pa = os.listdir(spacy_path) # spacy pubannotation files

def cord_uids():
    '''
    Return a list of cord_uids for the articles that have an abbreviation list.
    '''
    abbrv_corduid = [] # cord_uid for articles that have an abbreviation list
    for f in scrape_abbrv:
        abbrv_corduid.append(f[:-17])
    
    return abbrv_corduid

def get_article(cord_uid):
    '''
    Return the sha.json (orginal json file name for articles) for articles with cord_uid from metadata_comm_use_subset_100.csv
    '''
    article = ''
    with open(metadata_path, 'r') as file:
        f = csv.reader(file)
        i = 0 # skip first header line
        for row in f:
            if i == 0:
                i = i+1
            else:
                if cord_uid == row[0]:
                    if '; ' in row[1]: # handle case with articles that have 2 different sha's
                        row[1] = row[1].split('; ')
                        for article in all_articles:
                            if row[1][0] == article[:-5]:
                                row[1] = row[1][0]
                            elif row[1][1] == article[:-5]:
                                row[1] = row[1][1]
                            else:
                                continue
                    article = row[1]+'.json'
    return article

def extract_text(article):
    '''
    Extract full text for articles and extract the abbreviations with the spaCy abbreviation detector
    Return dictionary of abbreviations
    '''
    full_text = []
    title = PubAnnotationGenerator.get_title(article)
    abstracts = PubAnnotationGenerator.get_abstract(article)
    body_texts = PubAnnotationGenerator.get_body_text(article)
    abstract = ''.join(abstracts)
    body_text = ''.join(body_texts)
    full_text.append(title)
    full_text.append(abstract)
    full_text.append(body_text)
    full_text = ''.join(full_text)
    return full_text
def spacy_csv(cord_uid, abbreviations):
    output_path = '/mnt/c/Users/Sonja/OneDrive/Dokument/Skola/Projektkurs/edan70/data/spacy_abbr/'
    csv_header = ['Short form', 'Long form']
    j = 0
    data = []
    for i in range(len(abbreviations)):
            short_form = abbreviations[i]
            #print("short_form: ", short_form)
            long_form = abbreviations[i]._.long_form
            #print("long_form: ", long_form)
            data.append({'Short form': short_form, 'Long form': long_form})
    csv_name = cord_uid +'-spacy_abbr.csv'
    try:
        with open(output_path + csv_name, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_header)
            writer.writeheader()
            for d in data:
                writer.writerow(d)
        i = i+1
    except IOError:
        print("I/O Error") 
    return csv_name

def main():
    cuid = cord_uids() # list of cord_uid for articles that have abbreviation list

    for c in cuid:
        article = get_article(c)
        full_text = extract_text(article)
        abbreviations = PubAnnotationGenerator.get_abbreviations(full_text)
        spacy_file = spacy_csv(c, abbreviations)
        print("cord_uid: ", c, "gave out file: ", spacy_file)
 

if __name__ == "__main__":
    main()

