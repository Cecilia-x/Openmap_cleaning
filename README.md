# Openmap Data Cleaning Project
A training project of Clearning openmap data

## Purpose of Project
Auditing the openmap data in tsv formmat, cleaning data with error input or ununified formmating, and write to SQL database.

## Steps
### audit.py
Explore and inspect format of data. 

### closer_insepect_values.py
Closer inspect the values of certain tags. For each tag with key value in 'target' list, collect and write JSON file.

### inspect_keys.py
Inspect keys, expecially keys with colon.

### view_problems_keys.py
Collect tags with keys that probably contain problem chars.
It will examin each tag key in each element. If one tag key contain problem chars
or have colon but not fit the pattern, then get all the tags.

### insepct_names.py
Go through all the tag keys like 'name:languagecode', and inspect.
if all language code in the name are in the ISO-639 language standard.
For each outliner founded, collect their values and write to output file.

### inspect_address.py
Inspect tags with address key.

## Problems founded
### Problems in tag keys:
*1	Space in key( k="name:中文 Jade Court" )     
*2  Ununified language code for name keys (name:zht, name:zh-tradiction, name:zh_classical)    
### Problems in tag values:
*3 Strings in numeric values (1, 1 level, 1层, 底层; 1234 and 1,234)    
*4 Number in logical values (yes, no, 1)    
*5 Wrong start date (“2027”)    
*6 Wrong format of postcode (SL 202, 0000)    
*7 Ununified format of phone and fax (“020 2222 2222”, “+86 20 2222 2222”)   
*8 Abbreviation in street name(“Rd.”)    

## Soluction and database
### solutions.py
Different solution for types of problems.

## Reference
(1)Hongkong characters set: 
https://www.ogcio.gov.hk/en/business/tech_promotion/ccli/hkscs/2008_summay.htm     
(2)ISO-639 standard: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes, http://www-01.sil.org/iso639-3/codes.asp 


