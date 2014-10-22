@echo off
echo Generating application translation strings...
python pygettext.py -v -d "The Qube" ../src/*.pyw ../src/*.py ../src/*/*.py ../src/*/*.pyw ../src/*/*/*.py ../src/*/*/*.pyw ../src/*/*/*/*.py ../src/*/*/*/*.pyw ../src/*/*/*/*/*.py ../src/*/*/*/*/*.pyw ../src/*/*/*/*/*/*.py ../src/*/*/*/*/*/*.pyw ../src/*/*/*/*/*/*/*.py ../src/*/*/*/*/*/*/*.pyw ../src/*/*/*/*/*/*/*/*.py ../src/*/*/*/*/*/*/*/*.pyw
echo Done.