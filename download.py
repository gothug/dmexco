import logging
import requests
from bs4 import BeautifulSoup
import sys

logger = logging.getLogger(__name__)

def get_categories(cat_div):
    # put all cat codes in one list
    cat_codes = []
    for code in cat_div.find_all('dt'):
        cat_codes.append(code.get_text())
    # put all cat names in one list
    cat_names = []
    for cat in cat_div.find_all('dd'):
        cat_names.append(cat.get_text())
    # put together cat codes and cat_names
    cats = []
    if len(cat_codes) == len(cat_names):
        for i in range(len(cat_codes)):
            cats.append(cat_codes[i] + cat_names[i])
    else:
        print('different length of cat_codes and cat_names ')
    return cats


def boil_soup(url):
    r = requests.get(url)
    if r.status_code != 200:
        sys.exit('request code fur ulr ' + url + ' is ' + str(r.status_code))
    content = r.text
    soup = BeautifulSoup(content, 'html.parser')
    return soup

def get_exh_ids():
    logger.info("Getting ids of exhibition desks..")
    ids = []
    page_ex  = 'http://goo.gl/gl7Ars'
    soup = boil_soup(page_ex)
    e_links = soup.find_all(title='Show exhibitor information')
    # get all exh ids in one list
    for j in range(len(e_links)):
        if j % 2 == 0:
            href = e_links[j].get('href')
            un = href[href.rfind('exh_id=') + 7:]
            ids.append(un)
    logger.info("Total ids found: %s" % len(ids))
    return ids

def get_exh_data(id):
    def string_is_hall_place(string):
        result = False
        halls_names = ['Hall', 'hall', 'Start-up Village']
        for name in halls_names:
            if string[:len(name)] == name:
                result = True
                break
        return result

    exh_href = "https://service.dmexco.de/km_vis-cgi/km_vis/vis/custom/ext2/show_exhibitor_data.cgi?data_area=products&ticket=k0846607304819&exh_id="
    soup = boil_soup(exh_href + id)
    exh_data = soup.find_all(attrs={"class": "c58l"})[0]
    try:
        exh_cat = soup.find_all(attrs={"class": "prod_list"})[0]
    except:
        exh_cat = None
    link_name, hall_place, phone, fax, website, mail, cats = '', '', '', '', '', '', ''
    data_list = []
    for string in exh_data.stripped_strings:
        data_list.append(string)
    link_name = data_list[0]
    hall_place = data_list[1]
    if not string_is_hall_place(hall_place):
        hall_place = data_list[2]
        if not hall_place:
            print(data_list[1], '     ', data_list[2], 'NO HALL PLACE')
            sys.exit()
        else:
            link_name += ' ' + data_list[1]
            data_list.pop(1)
            hall_place = data_list[1]


    for el in data_list:
        if el[:len('Phone')] == 'Phone':
            phone = el[7:]
        elif el[:len('Fax')] == 'Fax':
            fax = el[5:]
        elif el[:len('http')] == 'http':
            website = el
        elif el[:len('JSCrypt.write')] == 'JSCrypt.write':
            str_with_mail = el
            at_pos = str_with_mail.rindex('@')
            mail_st_pos = str_with_mail.rindex('>', 0, at_pos)
            mail_en_pos = str_with_mail.index('<', at_pos, len(str_with_mail))
            mail = str_with_mail[mail_st_pos + 1 :mail_en_pos]
    address = data_list[2] + ' ' + data_list[3] + ' ' + data_list[4]
    if exh_cat != None:
        for el in get_categories(exh_cat):
            cats += el + '|'
        cats = cats[:-1]
    data_row = [id, link_name, address, phone, fax, website, mail, cats]

    return data_row
