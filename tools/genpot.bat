@echo off
echo Generating application translation strings...
python pygettext.py -v -d "TheQube" ../src/*.pyw ../src/*.py ../src/*/*.py ../src/*/*.pyw ../src/*/*/*.py ../src/*/*/*.pyw ../src/*/*/*/*.py ../src/*/*/*/*.pyw ../src/*/*/*/*/*.py ../src/*/*/*/*/*.pyw ../src/*/*/*/*/*/*.py ../src/*/*/*/*/*/*.pyw ../src/*/*/*/*/*/*/*.py ../src/*/*/*/*/*/*/*.pyw ../src/*/*/*/*/*/*/*/*.py ../src/*/*/*/*/*/*/*/*.pyw
echo Done.