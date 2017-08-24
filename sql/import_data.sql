set autocommit=0;
use openmap;
load data infile 'nodes_tags.csv'
INTO TABLE nodes_tags
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'

IGNORE 1 ROWS
(id, `key`, value, type);
commit;
