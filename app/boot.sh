python3 manage.py migrate --check

# check for unapplied migrations
if [ $? -ne 0 ]
then
  python manage.py migrate

  # check for a good exit
  if [ $? -ne 0 ]
  then
    # something went wrong; convey that and exit
    exit 1
  fi

  ./import_fixtures.sh

  # check for a good exit
  if [ $? -ne 0 ]
  then
    # something went wrong; convey that and exit
    exit 1
  fi

fi
