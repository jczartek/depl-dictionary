gnome = import('gnome')

resources = gnome.compile_resources(
  'depl-dictionary',
  'depl-dictionary.gresources.xml',
  gresource_bundle: true,
  install: true,
  install_dir: get_option('prefix')
)

install_data('depl-dictionary.py', install_dir: get_option('prefix'))
install_data('depl-dictionary.plugin', install_dir: get_option('prefix'))
