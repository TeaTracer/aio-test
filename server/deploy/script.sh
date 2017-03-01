#!/bin/sh

#####################################

MY_PATH=$(pwd)
SCRIPT_PATH=$( cd "$(dirname "$0")" ; pwd -P )
cd "$MY_PATH"

#####################################

PROJECT="aio-test"
DATABASE='aio'
SCHEMA='aio'
DBUSER='admin'
DBPASSWORD='admin'
LOG="/var/log/$PROJECT-deploy.log"
REPOSITORY="https://github.com/TeaTracer/$PROJECT.git"
ENV=".venv/bin/activate"
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color
NGINX_FROM="${SCRIPT_PATH}/nginx.conf"
NGINX_TO="/etc/nginx/sites-available/default"

#####################################

log() {
    "$@" 2>&1 | sudo tee -a $LOG > /dev/null
}

colorlog() {
    local color="$1"
    echo $color $(date -u) "|" $2 $NC | tee /dev/tty | sed 's/\x1B\[[0-9;]*[JKmsu]//g' | sudo tee -a $LOG > /dev/null
}

oklog() {
    colorlog "$GREEN" "$1"
}

faillog() {
    colorlog "$RED" "$1"
}

ensure() {
    if [ $# -eq 3 ]; then
        local task="$3"
        ($1)  # test
        if [ $? -ne 0 ]; then
            oklog "$task start"
            ($2)  # fix function
            ($1)  # second test
            if [ $? -ne 0 ]; then
                faillog "$task fail"
                exit 1  # can't do anything
            fi
        else
            oklog "$task already done"
        fi
        oklog "$task success"
    else
        faillog "EnsureError"
        exit 1
    fi

}

test_locale() {
    locale -a | grep "en_US.utf8" > /dev/null
}

fix_locale() {
    oklog "Change locale to en_US.UTF-8"
    log sudo locale-gen en_US.UTF-8
    log sudo update-locale en_US.UTF-8
}

test_postgres() {
    local resval="$(psql -V 2> /dev/null)"
    if [ $? -eq 0 ]; then
        local pg_version="$(echo $resval | awk '{print substr($NF, 1, 3)}')"
        local enc="$(sudo -u postgres psql -c 'show server_encoding;' 2> /dev/null | head -3 | tail -1 | awk '{print $1}')"
        if [ "$pg_version" = "9.6" ] && [ "$enc" = "UTF8" ]; then
            return 0
        fi
    fi
    return 1
}

fix_postgres() {
    log sudo apt-get install -y postgresql-9.6 pgadmin3 postgresql-server-dev-9.6
    log sudo pg_dropcluster --stop 9.6 main
    log sudo pg_createcluster --locale en_US.UTF-8 --start 9.6 main
    echo "postgres:postgres" | sudo chpasswd
    log sudo sed -i.bak 's/^\(local\ *all\ *postgres\ *\)peer$/\1md5/' /etc/postgresql/9.6/main/pg_hba.conf
    log sudo service postgresql restart

}

test_database() {
    sudo -u postgres psql -q -d $DATABASE -v ON_ERROR_STOP=1 -c "select 2+2;" > /dev/null 2>&1
    sudo -u postgres psql $DATABASE -c "select schema_name from information_schema.schemata;" | grep $SCHEMA 2> /dev/null 1>&2

}

fix_database() {
    log sudo -u postgres createuser -a -s -d $DBUSER 2> /dev/null
    log sudo -u postgres psql -q -c "alter user \"$DBUSER\" with password '$DBPASSWORD';" 2> /dev/null
    log sudo -u postgres psql -q -c "create database $DATABASE" 2> /dev/null
    log sudo -u postgres psql $DATABASE -q -c "create schema $SCHEMA;" 2> /dev/null
    log sudo -u postgres psql -q -c "grant all privileges on database $DATABASE to $DBUSER;" 2> /dev/null
    log sudo -u postgres psql -q -c "revoke all on schema public from public;" 2> /dev/null
}

test_python_ppa() {
    find /etc/apt/ -name *.list | xargs cat | grep "python" > /dev/null
}

fix_python_ppa() {
    log sudo add-apt-repository ppa:jonathonf/python-3.6 -y
}

test_python() {
    python3.6 -c '' 2> /dev/null
}

fix_python() {
    log sudo apt-get install python3.6 python3.6-dev -y
}

test_virtualenv() {
    if [ -f "$ENV" ]; then
        . $ENV
        local pip_python_version="$(pip -V | awk '{print substr($NF, 1, 3)}')"
        if [ "$pip_python_version" = "3.6" ]; then
            return 0
        fi
    fi
    return 1
}

fix_virtualenv() {
    log python3.6 -m venv --without-pip .venv
    . .venv/bin/activate
    log curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
    log python3.6 get-pip.py
    log rm get-pip.py
}

test_nginx() {
    if [ -f $NGINX_FROM ] && \
       [ -f $NGINX_TO ] && \
       [ $(cmp -s $NGINX_FROM $NGINX_TO 2>/dev/null; echo $?) -eq 0 ] && \
       [ $(sudo nginx -t 2> /dev/null; echo $?) -eq 0 ]; then
        return 0
    fi
    return 1
}

fix_nginx() {
    log sudo apt-get install nginx -y
    log sudo cp $NGINX_FROM $NGINX_TO
}

test_gcc() {
    hash gcc 2> /dev/null
}

fix_gcc() {
    log sudo apt-get install gcc -y
}

test_ssl() {
    if [ -f "/etc/ssl/server.crt" ] && \
       [ -f "/etc/ssl/server.key" ] && \
       [ $(openssl -h 2> /dev/null; echo $?) -eq 0 ]; then
            return 0
    fi
    return 1
}

fix_ssl() {
    (cd "$SCRIPT_PATH" && log sudo ./ssl.sh 2> /dev/null)
    log sudo apt-get install openssl -y 2> /dev/null
}

test_postgres_ppa() {
    find /etc/apt/ -name *.list | xargs cat | grep "postgresql" > /dev/null
}

fix_postgres_ppa() {
    sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
    log sudo apt-get install wget ca-certificates
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | log sudo apt-key add -
}


update () {
    oklog "Apt-get update"
    log sudo apt-get update -y
}


#####################################

oklog "Start deploying."

ensure test_locale fix_locale "Locale en_US.utf-8 installation"
ensure test_python_ppa fix_python_ppa "Python ppa installation"
ensure test_postgres_ppa fix_postgres_ppa "Postgres ppa installation"
update
ensure test_python fix_python "Python 3.6 installation"
ensure test_virtualenv fix_virtualenv "Virtualenv installation"
ensure test_ssl fix_ssl "SSL installation"
ensure test_nginx fix_nginx "Nginx installation"
ensure test_gcc fix_gcc "GCC installation"
ensure test_postgres fix_postgres "Postgres installation"
ensure test_database fix_database "Database creation"

oklog "Finish deploying."

#####################################
