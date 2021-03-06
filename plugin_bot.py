import logging
import os
from functools import wraps
from importlib import import_module
from inspect import signature
from re import match

from telegram.ext import Updater

PLUGINS = {}
PASSABLE = {'plugins': lambda: PLUGINS,
            'logger':  lambda: logger}

updater = Updater(token="PLACEHOLDER")

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Find plugins in their directories and add them to the PLUGINS dictionary.
for directory in (s for s in os.listdir('plugins') if os.path.isdir('plugins/' + s)):
    for fn in (s[:-3] for s in os.listdir('plugins/' + directory) if s.endswith('.py')):
        plugin = import_module(f'plugins.{directory}.{fn}')

        name = match(r'plugin:([\w\s]+)', plugin.__doc__ or '')
        if name:
            PLUGINS[name.group(1)] = plugin


def pass_globals(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        sig = signature(f).parameters
        return f(*args, **{k: v() for k, v in PASSABLE.items() if k in sig}, **kwargs)

    return wrapper


# Load plugins in specified order.
for k in sorted(PLUGINS, key=lambda k: PLUGINS[k].order if hasattr(PLUGINS[k], 'order') else 0):
    if hasattr(PLUGINS[k], 'handlers'):
        for h in PLUGINS[k].handlers:
            if not isinstance(h, list):
                h = [h]

            # Wrap callback function with globals if required.
            if any(a in PASSABLE for a in signature(h[0].callback).parameters):
                h[0].callback = pass_globals(h[0].callback)

            updater.dispatcher.add_handler(*h)

    logger.info(f'loaded plugin "{k[0]}"')


def err(bot, update, error):
    logger.error(f'update "{update}" caused error "{error}"')


updater.dispatcher.add_error_handler(err)
updater.start_polling()
