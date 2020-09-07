--install:
sudo python setup.py install --install-layout=deb
sudo cp clients/cli/rabbitvcs /usr/bin

--check files with locale/getlocale/gettext:
rabbitvcs/rabbitvcs/ui/widget.py
rabbitvcs/rabbitvcs/util/strings.py
rabbitvcs/rabbitvcs/ui/settings.py
rabbitvcs/rabbitvcs/util/helper.py
rabbitvcs/rabbitvcs/services/checkerservice.py
rabbitvcs/rabbitvcs/util/_locale.py
rabbitvcs/rabbitvcs/ui/__init__.py
rabbitvcs/rabbitvcs/vcs/git/__init__.py
rabbitvcs/rabbitvcs/__init__.py
rabbitvcs/clients/cli/rabbitvcs
