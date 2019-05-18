import importlib

REGISTERED_MODULES = [
    'core',
    'cccc',
    'texts',
    'urls',
]

for x in REGISTERED_MODULES:
    importlib.import_module('.%s' % x, __package__)
