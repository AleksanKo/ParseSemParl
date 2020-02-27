from os import listdir
from os.path import isfile, join
from parse_example import extracting_data_from_doc
mypath = 'C:/Users/konovale/Parsing/data_txt/'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
texts = []

for i in onlyfiles:
    with open(mypath+i,'r', encoding='utf-8') as f:
        extracting_data_from_doc(mypath+i)

#скопипастить отсюда http://www.kielitoimistonohjepankki.fi/ohje/262 список сокращений и отчипывать их от имени
#или просто искать сразу же 
# abbreviations = {
#     'Eläinoikeuspuolue':'eop',
#     'Feministinen puolue':'fp',
#     'Itsenäisyyspuolue':'ipu',
#     'Kansalaispuolue':'kp',
#     'Kansallinen Kokoomus':'kok',
#     'Liberaalipuolue - Vapaus valita':'lib',
#     'Liike Nyt': 'liik',
#     'Perussuomalaiset':'ps',
#     'Piraattipuolue':'pp',
#     'Seitsemän tähden liike':'tl',
#     'Sininen tulevaisuus':'sin',
#     'Suomen Kansa Ensin':'ske',
#     'Suomen Keskusta':'kesk',
#     'Suomen Kristillisdemokraatit (KD)':'kd',
#     'Suomen ruotsalainen kansanpuolue':'r',
#     'Suomen Sosialidemokraattinen Puolue':'sd',
#     'Vasemmistoliitto':'vas',
#     'Vihreä liitto':'vihr',
#     'Kommunistinen Työväenpuolue – Rauhan ja Sosialismin puolesta':'ktp',
#     'Suomen Kommunistinen Puolue':'komm',
#     'Reformi':'ref'}