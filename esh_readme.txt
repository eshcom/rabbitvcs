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
Менеджер веток:		manager.xml			branches.py
Менеджер тэгов:		manager.xml			tags.py


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


--color example:
for n, log in enumerate(self.log_by_order):
	setattr(log, "n", n)
	c = self.randomHSL()
	c = helper.HSLtoRGB(*c)
	setattr(log, "background", helper.html_color(*c))
	self.log_by_revision[self.short_revision(log.revision)] = log
	author = S(log.author.strip())
	if author:
		c = self.randomHSL()
		c = helper.HSLtoRGB(*c)
		self.author_background[author] = helper.html_color(*c)

def randomHSL(self):
	return (uniform(0.0, 360.0), uniform(0.5, 1.0), LUMINANCE)

def HSLtoRGB(h, s, l):
	"""
	Convert a color from the HSL space to RGB.
	@type   h: (int, float)
	@param  h: Hue in degrees.
	@type   s: float
	@param  s: Saturation in range 0.0 to 1.0
	@type   l: float
	@param  l: Luminance in range 0.0 to 1.0
	"""
	if not 0.0 <= s <= 1.0:
		raise ValueError("Saturation should be >= 0.0 and <= 1.0")
	if not 0.0 <= l <= 1.0:
		raise ValueError("Luminance should be >= 0.0 and <= 1.0")

	if s == 0.0:
		return (0, 0, 0)

	sextant = h % 360.0 / 60.0
	c = (1.0 - abs(2.0 * l - 1.0)) * s
	x = (1.0 - abs(sextant % 2.0 - 1.0)) * c
	m = l - c / 2.0
	i = int(sextant)
	r = [c, x, 0.0, 0.0, x, c][i]
	g = [x, c, c, x, 0.0, 0.0][i]
	b = [0.0, 0.0, x, c, c, x][i]
	return (int((v + m) * 255.0) for v in (r, g, b))

def html_color(r, g, b, a=None):
	fmt = "%02X"
	alpha = a or 0
	if r < 0x10 and g < 0x10 and b < 0x10 and alpha < 0x10:
		fmt = "%01X"
	color = (fmt * 3) % (r, g, b)
	if not a is None:
		color += fmt % a
	return "#" + color
