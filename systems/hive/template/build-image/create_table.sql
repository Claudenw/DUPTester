create table table (id int,name string) row format delimited fields terminated by ',';

LOAD DATA LOCAL INPATH '/data.txt' OVERWRITE INTO TABLE table;  

