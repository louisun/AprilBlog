#!/bin/bash
#
# Useage:
#   Auto deploy site to apache.
#

source ~/sh-realpath/realpath.sh

echo `whoami`

cd "$(dirname $0)"

SCRIPT=`realpath $0`

BASE_DIR=`dirname ${SCRIPT}`

PYENV=`realpath ${BASE_DIR}/../BlogEnv/bin/activate`

source "$PYENV"

PYTHON_SITE_PACKAGE=`python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"`

if [ ! -f 'db.sqlite3' ]; then
    # first deploy
    IS_FIRST_DEPLOY=true
else
    IS_FIRST_DEPLOY=false
fi

# update repo
git pull

# update database
python3 manage.py migrate

# Is first deploy, configure apache
if [ "${IS_FIRST_DEPLOY}" = true ]; then
    rc=1
    while [ ${rc} != 0 ]; do
        python3 manage.py createsuperuser
        rc=$?
    done
    sed -e "s#%BASE_DIR%#${BASE_DIR}#" -e "s#%PY_LIB%#$PYTHON_SITE_PACKAGE#" deploy/apache.conf.template > "roadsheep.com.conf"
    sudo mv -f "roadsheep.com.conf" "/etc/apache2/sites-available/roadsheep.com.conf"
    sudo a2ensite roadsheep.com
    sudo service apache2 reload
    sudo chown -R :www-data .
    sudo chown :www-data db.sqlite3
fi

# apache reload
touch AprilBlog/wsgi.py