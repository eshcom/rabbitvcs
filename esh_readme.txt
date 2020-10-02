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
Обновить:			git-update.xml		update.py
Зафиксировать:		commit.xml			commit.py, createpatch.py
Залить:				push.xml			push.py
Откатить:			revert.xml			revert.py
Очистить:			clean.xml			clean.py
Сбросить:			reset.xml			reset.py
Извлечь:			update.xml			updateto.py
Экспорт:			checkout.xml		checkout.py
Объединить:			branch-merge.xml	merge.py
Показать изменения:	changes.xml			changes.py


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


--dialog confirm example1:
confirm = rabbitvcs.ui.dialog.Confirmation(
	_("Are you sure you want to clear your repository paths?")
)
if confirm.run() == gtk.RESPONSE_OK:
	path = helper.get_repository_paths_path()

--dialog confirm example2:
confirm = rabbitvcs.ui.dialog.Confirmation(
	_("Are you sure you want to delete %s?" % ", ".join(selected)))
result = confirm.run()
if result == gtk.RESPONSE_OK or result == True:
	self.load(self.show_add)
