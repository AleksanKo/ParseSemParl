from os import listdir
from os.path import isfile, join
import json
import re
import requests
from bs4 import BeautifulSoup, Tag, NavigableString
import pandas as pd

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
            json_data = json.loads(response.content)
            jsons.append(json_data)
        print('{} JSONs gathered'.format(len(jsons)))
    return jsons

def parsing_xml():
    json1 = download_jsons('folder')
    overall_data = []

    for xml in json1:
        for i in xml['rowData']:
            l2 = i[1]
            soup = BeautifulSoup(l2)
            #finding all speeches by tag
            items = soup.find_all("vsk:puheenvuorotoimenpide")

            all_dates = []
            all_times = []
            all_persons = []
            all_parties = []
            all_texts = []

            for i in range(0,len(items)):
                data_list = []
                #searching for attribute containing time of the beginning of the speech in format e.g. '2017-09-19T14:15:46'
                day = items[i]['vsk1:puheenvuoroaloitushetki']
                data_list.append(day)

                #gathering all necessary contents
                for j in items[i].descendants:
                    if isinstance(j, Tag):
                        for k in j.contents:
                            if isinstance(k, NavigableString):
                                data_list.append(k)
                overall_data.append(data_list)

    for data_list in overall_data:

        all_dates.append(data_list[0][0:10]) #because time is stored in format "2017-09-19T14:15:46"
        all_times.append(data_list[0][11:])

        #ministers don't have parties in data, so instead of the abbreviation 'minister' is appended
        if 'ministeri' in data_list[2]:
            all_persons.append(data_list[3] + ' ' + data_list[4])
            all_parties.append('minister')
        else:
            all_persons.append(data_list[2] + ' ' + data_list[3])
            all_parties.append(data_list[4])
        #we don't need the data about whether the speech is a response or some other type of speech, so we don't append it
        if 'puheenvuoro)' in data_list[5]:
            all_texts.append(' '.join(data_list[6:]))
        else:
            all_texts.append(' '.join(data_list[5:]))

    all_data = {'Date': all_dates,'Time': all_times, 'Speaker': all_persons, 'Party': all_parties,'Speech': all_texts}
    df = pd.DataFrame(all_data)
    return df

final_df = parsing_xml()
path = input('Enter a path to the CSV file where to save the data: ', )
final_df.to_csv(path, encoding='utf-8', sep='\t', mode='a', header=False)