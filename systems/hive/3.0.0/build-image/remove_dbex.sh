rm -rf /hive/data/metastore_db/dbex.lck
/hive/bin/schematool -dbType derby -upgradeSchema --verbose
/hive/bin/hive -f /read_data.sql
