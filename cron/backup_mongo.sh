#!/bin/sh

set -e

LOG_FILE="/var/log/mongo_backup.log"

DB='pmi'
DB_USER='pmi'
DB_PASSWORD='Title321'


DATE=`date +"%Y%m%d"`
PREV_DATE=`date --date '7 days ago' +"%Y%m%d"`
DAY=`date '+%a'`




echo "Remove old ${DB} data"
sudo rm -Rf /mysqlBackup/mysql_db_bak_${PREV_DATE}.sql


echo "Dumping MongoDB $DB database to compressed archive"
sudo /usr/bin/mongodump --db ${DB} --username ${DB_USER} --password ${DB_PASSWORD} --authenticationDatabase ${DB} --archive=/backup/mongo/${DB}_${DAY}.gz --gzip


echo "Backup Complete."

echo "[${USER}][`date`] : $DB Backup Compeleted $DATE - $DAY" >> ${LOG_FILE}
