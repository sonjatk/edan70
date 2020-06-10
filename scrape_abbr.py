'''
Script to iterate thorough aricles in comm_use_subset_100 and find those
that have an abbreviation list in the back_matter.
'''
import os
import json
import csv
import bs4
import requests

#load metadatafile
metadata_path = "/mnt/c/Users/Sonja/OneDrive/Dokument/Skola/Projektkurs/edan70/metadata_comm_use_subset_100.csv"
data_path = "/mnt/c/Users/Sonja/OneDrive/Dokument/Skola/Projektkurs/comm_use_subset_100/"
output_path = "/mnt/c/Users/Sonja/OneDrive/Dokument/Skola/Projektkurs/edan70/data/"

def extract_urls():
    '''
    Extract all the url's for the articles from the metadata_comm_use_subset_100.csv file.
    Return a list of the urls.
    '''
    urls = []
    with open(metadata_path, 'r') as file:
        f = csv.reader(file)
        i = 0
        for row in f:
            if i == 0:
                i = i+1
            else:
                urls.append(row[17]) # Change column number for the column number that the urls are located if another metadata file is used here
                i = i+1      
    return urls

def abbr_scrape(urls):
    '''
    Goes through all the urls from the input list. Scrapes the content of the webpage of the article with BeautifulSoup. 
    Looks for section titles in article that gives hit on any type of 'abbreviation' form to indicate that there is an abbreviation
    list section. Extract the content below this header depending on the format of the abbreviation lists. 
    Returns a disctionary with the url as key and the abbreviations in a list, where each index in the list is a list of the short and long form of abbreviation.
    '''
    abbr_urls = [] #list of urls with articles that give a hit on the 'abbreviation' search
    abbr_dict = {}
    i = 0
    for url in urls: 
        agent = {'User-Agent': 'Chrome/47.0.2526.83'} # change here depending on which web browser that is used
        source = requests.get(url, headers=agent) #extract source
        html_source = source.content
        soup = bs4.BeautifulSoup(html_source, 'html.parser')
        section = soup.find('h2', text={'Abbreviations', 'abbreviation', 'abbreviations', 'Abbreviation'})
        
        if section is not None:
            for s in section.find_next_siblings():
                if s.name == 'h2': # section is empty
                    break

                elif s.name == 'p': # if abbreviations are put in under the section as a plain text
                    string = s.text
                    abbrv = string.split('; ')
                    for i in range(len(abbrv)):
                        if ',' in abbrv[i]:
                            abbrv[i] = abbrv[i].split(', ')
                        else:
                            abbrv[i] = abbrv[i].split(': ')
                    abbr_dict[url] = abbrv

                elif s.findAll('tr') != []: # if abbreviations are put in under the section as a table
                    abbrv = []
                    for row in s.findAll('tr'):
                        columns = row.findAll('td')
                        output_row = []
                        for column in columns:
                            output_row.append(column.text)
                        abbrv.append(output_row)
                    abbr_dict[url] = abbrv
                else: # if abbreviations are put in under header in a different format
                    short_form = []
                    long_form = []
                    for abbr in s.findAll('dt'):
                        short_form.append(abbr.text)
                    for abbr in s.findAll('dd'):
                        long_form.append(abbr.text)
                    abbrv = []
                    for i in range(0, len(short_form)):
                        output_row = [short_form[i], long_form[i]]
                        abbrv.append(output_row)
                    abbr_dict[url] = abbrv

    #print(abbr_dict) 
    return abbr_dict 

def abbrv_csv(abbr_urls):
    '''
    Generates a csv file for each article in the subset that has an abbreviation list.
    Puts all found abbreviations with its short form in the first column and long form in the second.
    '''
    csv_heads = ['Short form', 'Long form']
    csv_name = ''

    with open(metadata_path,'r') as file:
        f = csv.reader(file)
        i = 0
        for row in f:
            if i == 0:
                i = i+1
            else:
                for k, v in abbrv_urls.items():
                    if k == row[17]:
                        data = []
                        csv_name = row[0] + '-abbreviation.csv'
                        for i in range(len(v)):
                            #print(v[i][0])
                            #print(v[i][1])
                            data.append({'Short form': v[i][0], 'Long form': v[i][1]})    
                        try:
                            with open(output_path + csv_name, 'w') as csvfile:
                                writer = csv.DictWriter(csvfile, fieldnames=csv_heads)
                                writer.writeheader()
                                for d in data:
                                    writer.writerow(d)
                        except IOError:
                            print("I/O Error")


def abbrv_metadata(abbrv_urls):
    '''
    Takes the dictionary with urls and the abbreviations found in the article at that url.
    Returns a csv file with the metadata columns "doi", "pmcid" and "pubmed_id" from the original metadata file.
    '''
    csv_header = ['doi', 'pmcid', 'pubmed_id']
    data = []
    with open(metadata_path,'r') as file:
        f = csv.reader(file)
        i = 0
        for row in f:
            if i == 0:
                i = i+1
            else:
                for k, v in abbrv_urls.items():
                    if k == row[17]:
                        data.append({'doi': row[4], 'pmcid': row[5], 'pubmed_id': row[6]})
    csv_name = 'metadata_comm_use_subset_100_abbr.csv'

    try:
        with open(csv_name, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = csv_header)
            writer.writeheader()
            for d in data:
                writer.writerow(d)
    except IOError:
        print('I/O Error')   



if __name__ == "__main__":
    urls = extract_urls()
    abbrv_urls = abbr_scrape(urls)
    abbrv_csv(abbrv_urls)
    abbrv_metadata(abbrv_urls)
