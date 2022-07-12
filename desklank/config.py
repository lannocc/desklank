from appdirs import AppDirs

from os.path import join, exists
from os import makedirs


DIRS = AppDirs('desklank', 'LANNOCC')

if not exists(DIRS.user_data_dir):
    makedirs(DIRS.user_data_dir)

def _load_(filename):
    config = join(DIRS.user_data_dir, filename)
    if not exists(config):
        return None

    with open(config, 'r') as config:
        return config.read()

def _save_(filename, txt):
    config = join(DIRS.user_data_dir, filename)

    with open(config, 'w') as config:
        config.write(txt or '')

def load_connect_label():
    return _load_('label')

def save_connect_label(label):
    _save_('label', label)

def load_connect_alias():
    return _load_('alias')

def save_connect_alias(alias):
    _save_('alias', alias)

def load_interests():
    config = _load_('interests')
    if config is None: return [ ]
    return config.split('\n')

def save_interests(interests):
    _save_('interests', '\n'.join(interests))

def load_peers():
    config = _load_('peers')
    if config is None: return [ ]
    return config.split('\n')

def save_peers(peers):
    _save_('peers', '\n'.join(peers))

