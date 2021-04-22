import os
import csv
import json
from matplotlib import pyplot as plt 
import numpy as np  

scrape_path_abbr = './data/scrape_abbr/'
spacy_path_abbr = './data/spacy_abbr/'
pa_path = './pubannotation/'

scrape_abbrv = os.listdir(scrape_path_abbr)
spacy_abbrv = os.listdir(spacy_path_abbr)
pa = os.listdir(pa_path) # list of pubannotation files

def compare_methods():
    '''
    Compares outputs for short and long form for the web scraping result against the spacy result.
    Uses the web scraping result as ground truth.
    '''
    stats_dict = {}
    for i in scrape_abbrv:
        for j in spacy_abbrv:
            if i.split('-')[0] == j.split('-')[0]:
                with open(spacy_path_abbr + j, 'r') as sp:
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
                s_hit = 0
                l_hit = 0
                for k1,v1 in sc_dict.items():
                    for k2,v2 in sp_dict.items():
                        if k1 == k2:
                            s_hit = s_hit + 1
                            if v1==v2:
                                l_hit = l_hit+1
                stat_s = s_hit/len(sc_dict)
                stat_l = l_hit/len(sc_dict)
                stats_dict[i.split('-')[0]] = [stat_s, stat_l]
    return stats_dict


def pa_abbrv_list():
    ''' 
    Return a list with PubAnnotation files belonging to articles that have abbreviation lists 
    '''
    pa_abbrv = []

    for c in spacy_abbrv:
        for p in pa:
            if c.split('-')[0] == p.split('-')[0]:
                pa_abbrv.append(p)
    return pa_abbrv

def nbr_denotations(pa_list):
    '''
    Returns a dictionary with cord_uid as key from the articles that have abbreviation lists.
    Value for each key is how many abbreviations that are registered as denotations in each PubAnnotation file
    for the articles.
    '''
    denotations_dict = {}
    
    for pa in pa_list:
        cord_uid = pa.split('-')[0]
        denotations_dict[cord_uid] = 0

    for pa in pa_list:
        for k, v in denotations_dict.items():
            if k == pa.split('-')[0]:
                with open(pa_path + pa) as file:
                    f = json.load(file)
                    if f["denotations"] != []:
                        nbr_d = len(f["denotations"])
                        denotations_dict[k] += nbr_d

    return denotations_dict

def nbr_spacy_abbrv(denotations_dict):
    '''
    Compares amount abbreviations detected with spacy for full text with the abbreviations detected
    and put in the denotations for each PubAnnotation file
    '''
    nbr_spacy = {} # number abbreviations detected in total with spacy on full text
    for sp in spacy_abbrv:
        for k,v in denotations_dict.items():
            if sp.split('-')[0] == k:
                with open(spacy_path_abbr + sp, 'r') as f:
                    spacy_file = csv.reader(f)
                    lines = len(list(spacy_file))
                    nbr_spacy[k] = lines - 1 # skip headers for columns
    
    return nbr_spacy

def comp_spacy_pa(denotations_dict, nbr_spacy):
    '''
    Compare amount abbreviations detected in the PubAnnotation files compared to the full text through spaCy.
    Using number abbreviations detected in full text as ground truth.
    '''
    stats_dict = {}
    for k1,v1 in denotations_dict.items():
        for k2,v2 in nbr_spacy.items():
            if k1 == k2:
                stats_dict[k1] = v1 / v2
    return stats_dict




def main():
    print("Stats for web vs full text with spacy")
    comp = compare_methods()
    print(comp)


    print("Stats for denotations classed as abbreviations vs full text with spacy")
    pa_list = pa_abbrv_list() # PubAnnotation files for articles with abbreviation lists
    denotations = nbr_denotations(pa_list)
    nbr_spacy = nbr_spacy_abbrv(denotations)
    stat = comp_spacy_pa(denotations, nbr_spacy)
    print(stat)


    short = []
    percent = 0
    for k,v in stat.items():
        short.append(v)
        percent += v
    
    mean = percent / 20
    print(mean)
    plt.hist(short, bins='fd')
    #plt.title("Abbreviations detected in sections of texts vs full text")
    plt.xlabel('r')
    plt.ylabel('number of articles')
    plt.show()
    plt.savefig('short.png')


if __name__ == "__main__":
    main()
