import os
import csv
import json
import spacy_detector
from matplotlib import pyplot as plt 
import numpy as np  
import pickle

SUBSET = 'comm_use_subset_100'
all_articles = os.listdir(SUBSET)

scrape_path_abbr = '/mnt/c/Users/Sonja/OneDrive/Dokument/Skola/Projektkurs/edan70/data/scrape_abbr/'
spacy_path = '/mnt/c/Users/Sonja/OneDrive/Dokument/Skola/Projektkurs/edan70/pubannotation/'
spacy_path_abbr = '/mnt/c/Users/Sonja/OneDrive/Dokument/Skola/Projektkurs/edan70/data/spacy_abbr/'
metadata_path = "/mnt/c/Users/Sonja/OneDrive/Dokument/Skola/Projektkurs/edan70/metadata_comm_use_subset_100.csv"


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

def pa_abbrv(abbrv_corduid):
    '''
    Put all the files which has its cord_uid in the file name in a list. 
    Return a list of all the pubannotation files that belong to the articles that have abbreviation lists
    in the article.
    '''
    spacy_abbrv = []

    for c in abbrv_corduid:
        #print("c ", c)
        for f in spacy_pa:
            #print("f ",f )
            if c in f:
                spacy_abbrv.append(f)
    #print(spacy_abbrv)
    return spacy_abbrv

def extract_dennotation(spacy_abbrv):
    '''
    Step through the articles in the spacy_abbrv list and see if the parts have denotations.
    Skip if no denotations exist, but if the part has denotations, run the spacy_detector.get_abbreviation(text)
    on the text in that section.
    If abbreviations exist then split the name to extract cord_uid for file and use that as a key in a dictionary where: {'cord_uid': [[a]}
    '''
    spacy_abbrv_dict = {}
    words = []
    for pa in spacy_abbrv:
        with open(spacy_path + pa) as file:
            f = json.load(file)
            words = []

            if f["denotations"] != []:
                cord_uid = pa.split('-')[0]
                if f["text"].find('\"') != -1:
                    f["text"] = f["text"].replace('\"', '')
    
                abbreviations = spacy_detector.get_abbreviations(f["text"])
                if abbreviations !=[]:
                    spacy_abbrv_dict[cord_uid] = []
                    for abrv in abbreviations:
                        spacy_abbrv_dict[cord_uid].append(abrv)
    return spacy_abbrv_dict
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
    title = spacy_detector.get_title(article)
    abstracts = spacy_detector.get_abstract(article)
    body_texts = spacy_detector.get_body_text(article)
    abstract = ''.join(abstracts)
    body_text = ''.join(body_texts)
    full_text.append(title)
    full_text.append(abstract)
    full_text.append(body_text)
    full_text = ''.join(full_text)
    return full_text
        
'''        
def spacy_csv(spacy_abbrv_dict):
    
    #Generate csv files for articles that have abbreviation list, put the abbreviations that were detected by spacy into the file.
    
    output_path = '/mnt/c/Users/Sonja/OneDrive/Dokument/Skola/Projektkurs/edan70/data/spacy_abbr/'
    csv_header = ['Short form', 'Long form']
    j = 0
    for k,v in spacy_abbrv_dict.items():
        data = []
        #print(k)
        for i in range(len(v)):
            short_form = v[i]
            #print("short_form: ", short_form)
            long_form = v[i]._.long_form
            #print("long_form: ", long_form)
            data.append({'Short form': short_form, 'Long form': long_form}) 
        csv_name = k +'-spacy_abbr.csv'
        try:
            with open(output_path + csv_name, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_header)
                writer.writeheader()
                for d in data:
                    writer.writerow(d)
            i = i+1
        except IOError:
            print("I/O Error")
    print("files generated: ", i)
'''

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
'''
def find_hits(cord_uids):
    spacy_abbrv = os.listdir('/mnt/c/Users/Sonja/OneDrive/Dokument/Skola/Projektkurs/edan70/data/spacy_abbr/')
    #scrape_abbrv = scrape_abbrv
    hist = []

    for c in cord_uids:
        for i in spacy_abbrv:
            for j in scrape_abbrv:
                if c == i.split('-')[0] and c == j.split('-')[0]:
                    with open(spacy_path_abbr + i, 'r') as sp:
                        with open(scrape_path_abbr + j, 'r') as sc:
                            sp_dict = {}
                            sc_dict = {}
                            spacy_file = csv.reader(sp)
                            scrape_file = csv.reader(sc)
                            k = 0
                            for row in spacy_file:
                                if k == 0:
                                    k = k+1
                                else:
                                    sp_short = row[0]
                                    sp_long = row[1]
                                    sp_dict[sp_short] = sp_long
                                    k = k+1
                            k = 0
                            for row in scrape_file:
                                if k == 0:
                                    k = k+1
                                else:
                                    sc_short = row[0]
                                    sc_long = row[1]
                                    sc_dict[sc_short] = sc_long
                                    k = k+1
                    #print("sp_dict: ", sp_dict)  
                    #print("len sc_dict: ", len(sc_dict), "sc_dict: ", sc_dict, )                 
                    hits = 0
                    for k1,v1 in sp_dict.items():
                        for k2,v2 in sc_dict.items():
                            if k1 == k2:
                                #print("The abbreviation ", k1, "and ", k2, "are both registered in article with cord_uid:", c)
                                hits = hits+1


                    #print("total amount of hits for cord_uid: ", c, "is", hits, "statistically: ", hits/len(sc_dict))
                    hist.append(hits/len(sc_dict))
                
    print(hist)
    #print("sp_dict: ", sp_dict, '\n')
    #print("sc_dict: ", sc_dict, '\n')
    #a = np.array(hist)
    print(hist)
    bins = [0,0.2,0.4,0.6,0.8,1]
    plt.hist(hist, bins)
    plt.title("Abbreviations detected spacy vs abbreviation lists")
    plt.show()
    plt.savefig('hist.png')
'''

def stats(cord_uid, spacy_file):
    for i in scrape_abbrv:
        if cord_uid == i.split('-')[0]:
            with open(spacy_path_abbr + spacy_file, 'r') as sp:
                with open(scrape_path_abbr + i, 'r') as sc:
                        sp_dict = {}
                        sc_dict = {}
                        spacy_file = csv.reader(sp)
                        scrape_file = csv.reader(sc)
                        k = 0
                        for row in spacy_file:
                            if k == 0:
                                k = k+1
                            else:
                                sp_short = row[0]
                                sp_long = row[1]
                                sp_dict[sp_short] = sp_long
                                k = k+1
                        k = 0
                        for row in scrape_file:
                            if k == 0:
                                k = k+1
                            else:
                                sc_short = row[0]
                                sc_long = row[1]
                                sc_dict[sc_short] = sc_long
                                k = k+1
    #print("sc: ", sc_dict)
    #print("sp: ", sp_dict)
    
    s_hit = 0
    l_hit = 0
    for k1,v1 in sc_dict.items():
        for k2,v2 in sp_dict.items():
            if k1 == k2:
                #print("The abbreviation ", k1, "and ", k2, "are both registered in article with cord_uid:", c)
                #print(k1, '=', k2)
                s_hit = s_hit + 1
                if v1==v2:
                    #print('\t', v1, '=', v2)
                    l_hit = l_hit+1
    stat_s = s_hit/len(sc_dict)
    stat_l = l_hit/len(sc_dict)
    return stat_s, stat_l

def main():
    cuid = cord_uids() # list of cord_uid for articles that have abbreviation list
    stat_dict = {}
    #full_text = extract_text('0969d53ac7a447d43b431dbe9744e416de26df38.json')
    #print(full_text)
    
    for c in cuid:
        article = get_article(c)
        full_text = extract_text(article)
        abbreviations = spacy_detector.get_abbreviations(full_text)
        #print("Article: ", article, '\n')
        #print("full_text: ", full_text, '\n')
        #print("abbreviations: ", abbreviations, '\n')
        spacy_file = spacy_csv(c, abbreviations)
        print("cord_uid: ", c, "gave out file: ", spacy_file)
        #print(spacy_file)
        stat_s, stat_l = stats(c,spacy_file)
        print('Results for article with cord_uid ', c, 'is', stat_s,'% for short form and ', stat_l,"% for long form")
        stat_dict[c] = [stat_s,stat_l]
    print("Total stats: ", stat_dict)
   

    #print(cuid)
    
    #print(extract_text(articles))
    #spa_abbrv = pa_abbrv(cuid) # list of pubannotation files for articles that have an abbreviation list
    #print(spa_abbrv)
    #spacy_abbrv_dict = extract_dennotation(spa_abbrv)
    #print(len(spacy_abbrv_dict))
    #spacy_csv(spacy_abbrv_dict) # make csv files for spacy abbrv files
    #find_hits(cuid)

if __name__ == "__main__":
    main()

