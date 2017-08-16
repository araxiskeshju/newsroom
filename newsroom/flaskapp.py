"""
Newsroom Flask app
------------------

This module implements WSGI application extending eve.Eve
"""

import os
import eve
import importlib

from superdesk.storage import AmazonMediaStorage, SuperdeskGridFSMediaStorage
from superdesk.datalayer import SuperdeskDataLayer
from content_api.tokens import SubscriberTokenAuth


NEWSROOM_DIR = os.path.abspath(os.path.dirname(__file__))


class Newsroom(eve.Eve):
    """The main Newsroom object."""

    def __init__(self, import_name=__package__, settings='settings.py',
                 **kwargs):
        """Override __init__ to do Newsroom specific config and still be able
        to create an instance using ``app = Newsroom()``
        """
        super(Newsroom, self).__init__(
            import_name,
            data=SuperdeskDataLayer,
            auth=SubscriberTokenAuth,
            settings=settings,
            template_folder=os.path.join(NEWSROOM_DIR, 'templates'),
            static_folder=os.path.join(NEWSROOM_DIR, 'static'),
            **kwargs)
        if self.config.get('AMAZON_CONTAINER_NAME'):
            self.media = AmazonMediaStorage(self)
        else:
            self.media = SuperdeskGridFSMediaStorage(self)
        self._setup_blueprints(self.config['BLUEPRINTS'])
        self._setup_apps(self.config['CORE_APPS'])

    def load_config(self):
        """Override Eve.load_config in order to get default_settings."""
        super(Newsroom, self).load_config()
        self.config.from_object('newsroom.default_settings')
        self.config.from_envvar('NEWSROOM_SETTINGS', silent=True)

    def _setup_blueprints(self, modules):
        """Setup configured blueprints."""
        for name in modules:
            mod = importlib.import_module(name)
            self.register_blueprint(mod.blueprint)

    def _setup_apps(self, apps):
        for name in apps:
            mod = importlib.import_module(name)
            if hasattr(mod, 'init_app'):
                mod.init_app(self)
