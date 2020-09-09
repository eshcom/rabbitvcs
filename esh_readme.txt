--install:
sudo python setup.py install --install-layout=deb
sudo cp clients/cli/rabbitvcs /usr/bin

--check files with locale/getlocale/gettext:
#?rabbitvcs/clients/cli/rabbitvcs
#rabbitvcs/rabbitvcs/__init__.py
#rabbitvcs/rabbitvcs/services/checkerservice.py
#rabbitvcs/rabbitvcs/ui/settings.py
rabbitvcs/rabbitvcs/ui/widget.py
#rabbitvcs/rabbitvcs/util/_locale.py

--ui-xml for windows (git commands):
Обновить:			git-update.xml
Зафиксировать:		commit.xml
Залить:				push.xml
Откатить:			revert.xml
Очистить:			clean.xml
Сбросить:			reset.xml
Извлечь:			update.xml
Экспорт:			checkout.xml
Объединить:			branch-merge.xml
Показать изменения:	changes.xml
