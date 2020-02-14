from os import listdir
from os.path import isfile, join
import json
import re
import requests
from bs4 import BeautifulSoup, Tag, NavigableString
import pandas as pd
from pprint import pprint

jsons = []

def download_jsons(mode):
    if mode == 'input':
        id_doc = input('Enter a document ID: ',)
        response = requests.get(
            'https://avoindata.eduskunta.fi/api/v1/tables/VaskiData/rows?perPage=10&page=0&columnName=Eduskuntatunnus&columnValue={}'.format(
                id_doc))
        json_data = json.loads(response.content)
        jsons.append(json_data)
    elif mode == 'folder':
        text_of_the_document = ''
        link = 'C:/Users/konovale/Parsing/data_txt/'
        onlyfiles = [f for f in listdir(link) if isfile(join(link, f))]
        id_search = re.compile('PTK\s\d{1,4}\/\d{4}\svp')
        ids = []
        texts = []
        for i in onlyfiles:
            with open(link + i, 'r', encoding='utf-8') as f:
                text_of_the_document = f.read()
                texts.append(text_of_the_document)
        for text in texts:
            id_doc = id_search.search(text).group()
            ids.append(id_doc)
        ids = list(set(ids))
        for id_doc in ids:
            response = requests.get('https://avoindata.eduskunta.fi/api/v1/tables/VaskiData/rows?perPage=10&page=0&columnName=Eduskuntatunnus&columnValue={}'.format(id_doc))
            #responses.append(response)
            json_data = json.loads(response.content)
            jsons.append(json_data)
        print('{} JSONs gathered'.format(len(jsons)))
    return jsons

json1 = download_jsons('folder')
alll_adata = []
print(json1)
print(len(json1))
for xml in json1:
    for i in xml['rowData']:
        l2 = i[1]
        soup = BeautifulSoup(l2)
        #t = str(l2)
        #if 'Alkoholijuomien anniskelu sallitaan' in t:
        #    print('wow this string is in xml')
        print(soup.prettify())
        items = soup.find_all("vsk:puheenvuorotoimenpide")
        #items = soup.findAll("sis:kappalekooste")
        print(len(items))
        day = soup.find("met1:nimeketeksti")
        print(day)
        date = re.search(r'\d{1,2}\.\d{1,2}.\d{4}',day.contents[0]).group()

        all_dates = []
        all_times = []
        all_persons = []
        all_parties = []
        all_texts = []

        for i in range(0,len(items)):
            data_list = []
            print('Now the list is empty')
            for j in items[i].descendants:
                print('For every descendant ', len(data_list))
                if isinstance(j, Tag):
                    for k in j.contents:
                        print('For every content', len(data_list))
                        if isinstance(k, NavigableString):
                            print('Now smth is appended')
                            data_list.append(k)
                            print('After append: ',len(data_list))
                        print('After if:', len(data_list))
                    print('After for contents',len(data_list))
                print('After Tag: ', len(data_list))
            print('After going desc', len(data_list))
            #print('After RANGE', len(data_list))
            alll_adata.append(data_list)
            #print(data_list)
        print(len(alll_adata))
for data_list in alll_adata:
    all_dates.append(date)
    all_times.append(data_list[0])
    if 'ministeri' in data_list[1]:
        all_persons.append(data_list[2] + ' ' + data_list[3])
        all_parties.append('minister')
    else:
        all_persons.append(data_list[1] + ' ' + data_list[2])
        all_parties.append(data_list[3])
    if 'puheenvuoro)' in data_list[4]:
        all_texts.append(' '.join(data_list[5:]))
    else:
        all_texts.append(' '.join(data_list[4:]))
print('persons',len(all_persons))
print('dates',len(all_dates))
print(len(all_dates)==len(all_persons))
all_data = {'Date': all_dates,'Time': all_times, 'Speaker': all_persons, 'Party': all_parties,'Speech': all_texts}
print(len(all_data))
df = pd.DataFrame(all_data)
print(df)
df.to_csv('C:/Users/konovale/Parsing/speeches_from_xml.csv', encoding='utf-8', sep='\t', mode='a', header=False)
# print(len(data_list))PTK 70/2019 vp


