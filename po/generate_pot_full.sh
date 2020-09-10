#!/bin/sh

# Sync our translation template file with the actual strings
# 1. Extracts strings from gtkbuilder xml files into .h files
# 2. Extracts gettext strings from py files
# 3. Deletes the glade .h files

cd ..

for i in `find . | grep '\.xml' | grep -v '\.svn' | grep -v '\.xml\.h'`;
do
	intltool-extract --type=gettext/glade $i
done

cd rabbitvcs

xgettext -L Python --keyword=_ --keyword=N_ -o ../po/RabbitVCS.pot -f ../po/POTFILES_full.in

for i in `find . | grep '\.xml\.h' | grep -v '\.svn'`;
do
	rm -f $i
done
