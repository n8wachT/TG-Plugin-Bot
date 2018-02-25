import functools
import json
import logging
import os
import re
from importlib import import_module
from inspect import signature

from telegram.ext import Updater

PLUGINS = {}

updater = Updater(token="PLACEHOLDER")

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

passable = {'plugins': 'PLUGINS', 'logger': 'logger'}

for directory in (s for s in os.listdir('plugins') if os.path.isdir('plugins/' + s)):
    for fn in (s[:-3] for s in os.listdir('plugins/' + directory) if s.endswith('.py')):
        plugin = import_module('plugins.{}.{}'.format(directory, fn))

        name = re.match(r'plugin:([\w\s]+)', plugin.__doc__)
        if name:
            PLUGINS[(name.group(1), plugin.order if hasattr(plugin, 'order') else 0)] = plugin


def pass_globals(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        for a in signature(f).parameters:
            if a in passable:
                kwargs[a] = globals()[passable[a]]

        return f(*args, **kwargs)

    return wrapper


for k in sorted(PLUGINS, key=lambda k: k[1]):
    if hasattr(PLUGINS[k], 'handlers'):
        for h in PLUGINS[k].handlers:
            if not isinstance(h, list):
                h = [h]
<<<<<<< HEAD

            if any(a in passable for a in signature(h[0].callback).parameters):
                h[0].callback = pass_globals(h[0].callback)
=======
                
            if any(a.name in passable for a in signature(h[0]).parameters):
                h[0] = pass_globals(h[0])
>>>>>>> d92336fc08cc9e5f0be8fe3d1ee9adbca5455c6d

            updater.dispatcher.add_handler(*h)

    logger.info('loaded plugin "{}"'.format(k[0]))


def err(update, error):
    logger.error('update "{}" caused error "{}"'.format(update, error))


updater.dispatcher.add_error_handler(err)
updater.start_polling()
