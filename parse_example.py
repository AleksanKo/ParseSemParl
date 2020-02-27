import re
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join
from tika import parser
from requests.exceptions import InvalidSchema, ChunkedEncodingError
"""
A script for extracting relevant data, namely date, time, a speaker, a speaker's party and a speech.
The data is written to dataframe and extracted to csv file.
"""
#downloading all texts from a file that contains links
def download_from_file():
    file_to_open = input('Enter a path to a file: ', )
    print(file_to_open)
    with open(file_to_open,'r') as f:
        list_of_files = f.readlines()
    list_of_files = list(filter(None,list_of_files))
    list_of_files = list(set(list_of_files))
    print(len(list_of_files))
    return list_of_files

#downloading jsons from VASKI dataset
def download_jsons():
    responses = []
    jsons = []
    page = int(input('Enter a number of pages: ', ))
    doc_type = input('Enter a type of the document: ', )
    for i in range(0,page+1):
        response = requests.get('https://avoindata.eduskunta.fi/api/v1/vaski/asiakirjatyyppinimi?perPage=100&page={}&languageCode=fi&filter={}'.format(i,doc_type))
        responses.append(response)
        json_data = json.loads(response.content)
        jsons.append(json_data)
    print('{} JSONs gathered'.format(len(responses)))
    return jsons

#downloading all files from jsons
def download_from_jsons():
    a_tags = []
    links = []
    jsons = download_jsons()

    for i in jsons:
        for j in i['rowData']:
            a_tags.append(j[5])

    print('Got {} tags'.format(len(a_tags)))

    for i in a_tags:
        soup = BeautifulSoup(i)
        l = soup.find('a').renderContents().decode('utf-8')[1:-1]
        links.append(l)

    print('Got {} links'.format(len(links)))

    links = list(filter(None,links))
    links = list(set(links))

    print('Filtered list, got {} links'.format(len(links)))
    
    file_to_write = input('Enter a path to a file: ',)
    with open(file_to_write,'w') as f:
        for i in links:
            f.write('%s\n' % i)

    for i in links:
        try:
            response_pdf = requests.get(i,timeout=1000)
            print('{} downloaded'.format(i[i.index('vaski'):i.index('.pdf')]))
            with open('Z:/Documents/New project/data/{}.pdf'.format(i[i.index('vaski'):i.index('.pdf')]),'wb') as file:
                file.write(response_pdf.content)
        except InvalidSchema or ChunkedEncodingError:
            print('Error in original data')    
            pass
    print('Wrote all files to pdf')

#пишем их в файл csv, в котором есть только хедеры
#надо зафигачить функцию для обработки каждого документа и потом вызывать ее для списка документов

def extracting_data_from_doc(link):

    text_of_the_document = ''

    with open(link, encoding='utf-8') as f:
        text_of_the_document = f.read()
    
    error_files = []
    #searching for a string that contains date in format 
    #"Day of the week + Date + 'klo' + Duration of the meeting"
    #Example: 'Torstai 19.9.2019 klo 15.59—19.13'
    date_search = re.compile(r'\w+\s\d{1,2}\.\d{1,2}.\d{4}\s\w{3,5}\s\d{1,2}\.\d{2}—\d{1,2}\.\d{2}')
    try:
        date_time = date_search.search(text_of_the_document).group()
    #gathering and storing date
    #for now duration of the meeting is not added to the dataframe
        for i in date_time:
            date = re.search(r'\d{1,2}\.\d{1,2}.\d{4}',date_time).group()

            #gathering all speeches (the text between from 'Discussion' to 'Discussion ended')
        possible_endings = ['Keskustelu päättyi','Kysymyksen käsittely päättyi']
        for i in possible_endings:
            try:
                all_speeches = text_of_the_document[text_of_the_document.index('Keskustelu'):
                                                        text_of_the_document.index(i)]


                    #removing page numbers and names of the document on every page
                all_speeches = re.sub(r'\d\n','', all_speeches)
                document_name_search = re.compile(r'([a-zA-Z0-9äöåÄÖÅ_\/]+\s)+[A-Z]+?\s\d{2,3}\/\d{4}\s+\w+?\n')
                all_speeches = re.sub(document_name_search,'',all_speeches)

                    #cleaning text from line separators
                all_speeches = all_speeches.replace('-\n',"")
                all_speeches = all_speeches.replace('\n'," ")
                all_speeches = all_speeches.replace('\r\n'," ")
                all_speeches = all_speeches.replace('  '," ")
                with open('C:/Users/konovale/Parsing//t1.txt','w') as f:
                    f.write(all_speeches)

                    #gathering data about speakers in format
                    #"Time + Title (optional) + Name+Surname + Party (optional) + Reply (optional)"
                    #Example: '16.15 Riikka Purra ps (vastauspuheenvuoro)', '16.13 Pääministeri Antti Rinne'
                speaker_search = re.compile(r'(\d{2}\.\d{2}(?:\s[A-ZÄÖÅÉ][a-zäöåé\-\'\,]+(?:\s[a-zäöåé\-\']+){1,4}){0,1}(?:\s[A-ZÄÖÅÉ][A-ZÄÖÅÉa-zäöåé\-\'\.]+){1,6}(?:\s[a-zäöå]{1,5}){0,1}\s{0,1}(?:\([a-zäöå]+(?:\s[a-zäöå]+){0,1}\)){0,1})')
                list_of_speakers = speaker_search.findall(all_speeches)
                print(list_of_speakers)

                all_dates = []
                all_times = []
                all_persons = []
                all_parties = []
                all_texts = []

                    #adding the data to lists
                for i in range(0,len(list_of_speakers)):
                    all_dates.append(date)
                    all_times.append(re.search(r'\d{2}\.\d{2}',list_of_speakers[i]).group())
                    all_persons.append(re.search(r'(?:\s[A-ZÄÖÅÉ][a-zäöåé\-\'\,]+(?:\s[a-zäöåé\-\']+){1,4}){0,1}(?:\s[A-ZÄÖÅÉ][A-ZÄÖÅÉa-zäöåé\-\'\.]+){1,6}',list_of_speakers[i]).group())
                    if re.search(r'\sja\s',list_of_speakers[i]):
                        all_parties.append('minister')
                    elif re.search(r'\soikeusasiamies\s',list_of_speakers[i]):
                        all_parties.append('ombudsman')
                    else:
                        try:
                            all_parties.append(re.search(r'\s[a-zäöå]{1,5}', list_of_speakers[i]).group())
                        except AttributeError:
                            all_parties.append('minister')
                    try:
                        all_texts.append(all_speeches[all_speeches.index(list_of_speakers[i])+len(list_of_speakers[i])+2:all_speeches.index(list_of_speakers[i+1])])
                    except IndexError:
                        all_texts.append(all_speeches[all_speeches.index(list_of_speakers[i])+len(list_of_speakers[i])+2:])

                    #checking that all lists have the same length
                print(len(all_dates), len(all_times), len(all_persons), len(all_texts), len(all_parties))
                    # print(all_dates[0])
                    # print(all_times[0])
                    # print(all_persons[0])
                    #print(all_texts[0])
                    # print(all_parties[0])
                    #написать Exception?

                    #writing all data to a dictionary and then to dataframe
                all_data = {'Date':all_dates, 'Time': all_times, 'Speaker':all_persons, 'Party':all_parties, 'Speech':all_texts}
                df = pd.DataFrame(all_data)

                    #checking the dataframe
                    #print(df.shape[0])

                    #writing a dataframe to csv
                #df.to_excel('C:/Users/konovale/Parsing/speeches_1.xlsx',encoding='utf-8')
                df.to_csv('C:/Users/konovale/Parsing/speeches_2end.csv', encoding='utf-8', sep='\t', mode='a', header=False)
            except ValueError:
                print('No discussion found in: {}'.format(link))
                pass
    except AttributeError:
        print('Some problems with date in {}'.format(link))
        error_files.append(link)
        print(len(error_files))
        with open('C:/Users/konovale/Parsing/errors.txt', 'w',encoding='utf-8') as f:
            for i in error_files:
                f.write(i)
        pass
#create a function
#def func():
#    mypath = 'Z:/Documents/New project/data/'
#    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
#    print(len(onlyfiles))
#    for i in onlyfiles:
#        try:
#            raw = parser.from_file('Z:/Documents/New project/data/{}'.format(i[i.index('vaski'):]))
#            with open('Z:/Documents/New project/data_txt/{}.txt'.format(i[i.index('vaski'):i.index('.pdf')]),'w', encoding='utf-8') as f:
#                f.write(raw['content'])
#        except ValueError:
#            pass

def creating_a_csv():
    dict_to_df = {'Date': [], 'Time': [] , 'Speaker': [], 'Party': [], 'Speech': []}
    df = pd.DataFrame(dict_to_df)
    df.to_csv('Z:/Documents/New project/speeches_all_test_fixed.csv',encoding='utf-8', sep='\t',mode='a', header=True)

#describe_a_function
def func1(): 
    mypath = 'Z:/Documents/New project/data_txt/'
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    print(len(onlyfiles))
    for i in onlyfiles:
        with open(i,'r', encoding='utf-8') as f:
            texts = f.read()
            extracting_data_from_doc(i)