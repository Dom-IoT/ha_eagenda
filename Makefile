# The name of the addon
ADDON_NAME = example_addon

# For old versions of Home Assistant, the addons directory is usually
# /usr/share/hassio/addons/local
# For current versions, the addons directory is
ADDONS_DIR = /var/lib/homeassistant/addons/local

# == DO NOT EDIT BELOW THIS LINE ==
# unless you know what you are doing

ANSIBLE_ARGS = --inventory ansible/inventory.yml ansible/playbook.yml --extra-vars "addon_name=$(ADDON_NAME)" --extra-vars "addons_dir=$(ADDONS_DIR)"

.PHONY: addon-setup addon-update addon-clean addon-reinstall swagger

addon-setup:
	ansible-playbook $(ANSIBLE_ARGS) --tags setup

addon-update:
	ansible-playbook $(ANSIBLE_ARGS) --tags update

addon-clean:
	ansible-playbook $(ANSIBLE_ARGS) --tags clean

addon-reinstall:
	ansible-playbook $(ANSIBLE_ARGS) --tags reinstall