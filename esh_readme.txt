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
