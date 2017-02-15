#!/bin/sh

#####################################

PROJECT="aio-test"
DATABASE='aio'
LOG="/var/log/$PROJECT-deploy.log"
# BRANCH="dev" # master or dev
REPOSITORY="https://github.com/TeaTracer/$PROJECT.git"
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

#####################################

oklog() {
    echo $GREEN $(date -u) "|" $1 $NC | sudo tee -a $LOG
}

faillog() {
    echo $RED $(date -u) "|" $1 $NC | sudo tee -a $LOG
}

create_database() {
    sudo -u postgres psql -q -v ON_ERROR_STOP=1  -c "create database $DATABASE;"
    if [ "$?" -gt "0" ]; then
      faillog "Postgres database '$DATABASE' creation fail."
    else
      oklog "Postgres database '$DATABASE' creation success."
    fi
}

test_postgres() {
    which psql > /dev/null
    if [ "$?" -gt "0" ]; then
      faillog "Postgres installation fail."
    else
      oklog "Postgres installation success."
      create_database
    fi
}

#####################################

oklog "Start deploying."

#####################################

oklog "Add PostgreSQL APT repository."
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
sudo apt-get install wget ca-certificates
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

#####################################

oklog "Change locale to en_US.UTF-8"
sudo locale-gen en_US.UTF-8
sudo locale-gen ru_RU.UTF-8
sudo update-locale en_US.UTF-8
export LC_ALL=en_US.UTF-8

#####################################

oklog "Update"
sudo apt-get update -y

#####################################

oklog "Installing PostgreSQL."
sudo apt-get install -y postgresql-9.6 pgadmin3
sudo pg_dropcluster --stop 9.6 main
sudo pg_createcluster --locale en_US.UTF-8 --start 9.6 main
echo "postgres:postgres" | sudo chpasswd
test_postgres

#####################################

oklog "Finish deploying."

#####################################
