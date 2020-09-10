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


--gsettings 1:
from gi.repository import Gio
gschema=Gio.Settings.new("org.gnome.desktop.interface")
gschema.get_value("text-scaling-factor")
gschema.get_double("text-scaling-factor")

--gsettings 2:
import os
os.system("gsettings get org.gnome.desktop.interface text-scaling-factor")

--gsettings 3:
import subprocess
eval(subprocess.check_output(["gsettings", "get", "org.gnome.desktop.interface", "text-scaling-factor"], universal_newlines=True))
