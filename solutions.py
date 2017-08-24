#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
This module contains functions needed to clean data, depending different feature
of data.
'''

import re

#These are solutions for formatting values.

def clear_space(v):
    return re.sub('\s', '', v)
    

def clear_comma(v):
    return  v.replace(',', '')

def clear_unit(v):
    return re.sub('\D', '', v)

def get_highest(v):
    l = v.split(',')
    num = 0
    for i in l:
        if type(i) == type(0) and i > num:
            num = i
    return num

            
def clear_phone(text):
    text = text.replace(u'＋','')
    text = re.sub('[\(\)]','',text)
    country, region, tel = '','',''
    country_pat = '(^86|^852|^853)'
    region_pat = '(^0??7\d{2}|^20|^020)'
    
    v2 = re.sub('^\+','',text)
    p = re.split('[\s\-]', v2)
    if len(p) in [4,5] and re.match(region_pat,p[1]) != None:
        country, region, tel = p[0],p[1],''.join(p[2:])
    elif len(p) == 3:
        if re.match(country_pat, p[0]) != None:
            country = p[0]
            if re.match(region_pat, p[1]) != None:
                region, tel = p[1],p[2]
            else:
                tel = ''.join(p[1:])
        else:
            if re.match(region_pat, p[0]) != None:
                region, tel = p[0], ''.join(p[1:2])
                country = '86'
    elif len(p) == 2:
        if re.match(country_pat, p[0]) != None:
            country = re.match(country_pat, p[0]).group()
            if len(p[0].replace(country,'')) > 0:
                region = p[0].replace(country,'')
            tel = p[1]
        else:
            region, tel = p[0],p[1]
            if re.match(region_pat, region) != None:
                country = '86'
    else:
        v2 = ''.join(p)
        if re.match(country_pat,v2) != None:
            country = re.match(country_pat,v2).group()
            v2 = v2.replace(country,"",1)
        if re.match(region_pat,v2) != None:
            region = re.match(region_pat,v2).group()
            tel = v2.replace(region,"",1)
            if country == '':
                country = "86"
        elif re.match('^1[3|5|7|8|]\d{9}',v2) != None:
            if country == '':
                country = "86"
            tel = v2
        else:
            tel = v2

    if country != "":
        country = '+{}'.format(country)
    if region != '' and region[0] in ['2','7'] and len(region) <= 3:
        region= "0" + region
    phone = []
    for i in [country, region, tel]:
        if i != '':
            phone.append(i)
    return ' '.join(phone)

def clear_multi_phones(text):
    if text.find(';') > -1:
        result = []
        phones = text.split(';')
        for phone in phones:
            result.append(clear_phone(phone))
        return ':'.join(result)
    else:
        return clear_phone(text)

def clean_level(v):
    v = v.replace(u'层','')
    try:
        v = int(v)
    except ValueError:
        if v.find('Gound') == 0:
            v = 1
        elif v == u'底':
            v = 1
    return v

def yes_to_num(v):
    if v.lower() == 'yes':
        v = 1
    return v

def num_to_log(v):
    if v == '-1':
        v = 'no'
    return v

def clear_name(name):
    if name == "name:":
        name = 'name'
    return name

def process_addr(address_tag):
    k, v = address_tag.attrib['k'], address_tag.attrib['v']
    addr_type = k.split(':',1)[1]
    if addr_type not in ['city', 'street', 'postcode', 'housenumber']:
        return None
    else:
        return {'key':addr_type, 'type':'addr', 'value':v}

def process_postcode(postcode):
    if re.match('^(51|52)\d{4}',postcode) != None:
        return postcode
    else:
        return ''

def process_date(text):
    if re.match('\d{4}',text):
        year = int(text[:4])
        if year >= 2017:
            return ''
        return text
    return ''

def clean_street(text):
    d = {'rd.':'road', 'Rd.':'road','str.':'street', 'Str.':'street'}
    for k in d.keys():
        text = text.replace(k, d[k])
    return text

# The mapping for tag keys and solutions for their values.

mapping_v = {
    'maxspeed' : clear_space,
    'catmp-RoadID' : clear_space,
    'gauge' : clear_comma,
    'ele' : clear_unit,
    'length' : clear_unit,
    'lanes' : clear_space,
    'garmin_road_class' : clear_space,
    'phone' : clear_multi_phones,
    'fax' : clear_multi_phones,
    'population' : clear_unit,
    'oneway' : num_to_log,
    'tunnel' : num_to_log,
    'level' : clean_level,
    'addr:postcode' : process_postcode,
    'start_data' : process_date,
    'addr:street' : clean_street
    }

# The mapping for unifying language of name.

mapping_name = {
    'zh-classical' : 'zh-hant',
    'zh-traditional' : 'zh-hant',
    'zn' : 'zh-hans',
    'zh_py' : 'zh-pinyin',
    'zh_yue' : 'yue',
    'zh-yue' : 'yue',
    'zh_pyt' : 'zh-pinyin',
    'zh-min-nan' : 'nan',
    'zh-Latn-pinyin' : 'zh-pinyin',
    'zh-simplified' : 'zh-hans',
    'cantonese' : 'yue',
    'int_name' : 'int',
    u'中中' : 'zh',
    u'中文 Jade Court' : 'zh',
    '"zh_jyutping' : 'zh',
    u'戈日' : 'zh'
    }

