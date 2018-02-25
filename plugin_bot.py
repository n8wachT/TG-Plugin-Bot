import functools
import json
import logging
import os
from importlib import import_module
from inspect import signature
from re import match

from telegram.ext import Updater

PLUGINS = {}
PASSABLE = {'plugins': 'PLUGINS', 'logger': 'logger'}

updater = Updater(token="PLACEHOLDER")

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Find plugins in their directories and add them to the PLUGINS dictionary with (name, order) tuples as keys.
for directory in (s for s in os.listdir('plugins') if os.path.isdir('plugins/' + s)):
    for fn in (s[:-3] for s in os.listdir('plugins/' + directory) if s.endswith('.py')):
        plugin = import_module('plugins.{}.{}'.format(directory, fn))

        name = match(r'plugin:([\w\s]+)', plugin.__doc__) if plugin.__doc__ else None
        if name:
            PLUGINS[(name.group(1), plugin.order if hasattr(plugin, 'order') else 0)] = plugin


def pass_globals(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        for a in signature(f).parameters:
            if a in PASSABLE:
                kwargs[a] = globals()[PASSABLE[a]]

        return f(*args, **kwargs)

    return wrapper


# Load plugins in specified order.
for k in sorted(PLUGINS, key=lambda k: k[1]):
    if hasattr(PLUGINS[k], 'handlers'):
        for h in PLUGINS[k].handlers:
            if not isinstance(h, list):
                h = [h]

            # Wrap callback function with globals if required.
            if any(a in PASSABLE for a in signature(h[0].callback).parameters):
                h[0].callback = pass_globals(h[0].callback)

            updater.dispatcher.add_handler(*h)

    logger.info('loaded plugin "{}"'.format(k[0]))


def err(bot, update, error):
    logger.error('update "{}" caused error "{}"'.format(update, error))


updater.dispatcher.add_error_handler(err)
updater.start_polling()
