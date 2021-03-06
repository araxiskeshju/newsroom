import superdesk

from flask import Blueprint, url_for
from flask_babel import gettext
from newsroom.wire.search import WireSearchResource, WireSearchService
from . import utils
from superdesk.metadata.item import not_analyzed

blueprint = Blueprint('wire', __name__)

from . import views  # noqa


def url_for_wire(item, _external=True):
    return url_for('wire.item', _id=item.get('_id', item.get('guid')), _external=_external)


def init_app(app):
    app.config['DOMAIN']['items']['schema'].update({
        'products': {
            'type': 'list',
            'mapping': {
                'type': 'object',
                'properties': {
                    'code': not_analyzed,
                    'name': not_analyzed
                }
            }
        },
        'agenda_id': {
            'type': 'string',
            'mapping': not_analyzed,
        },
    })

    superdesk.register_resource('wire_search', WireSearchResource, WireSearchService, _app=app)

    app.section('wire', 'Wire')

    app.sidenav('Home', 'wire.index', 'home')
    app.sidenav('Wire', 'wire.wire', 'text', section='wire')

    app.sidenav('Saved Items', 'wire.bookmarks', 'bookmark', group=1, blueprint='wire', badge='saved-items-count')

    from .formatters import TextFormatter, NITFFormatter, NewsMLG2Formatter, JsonFormatter
    app.download_formatter('text', TextFormatter(), gettext('Plain Text'), ['wire', 'agenda'])
    app.download_formatter('nitf', NITFFormatter(), 'NITF', ['wire'])
    app.download_formatter('newsmlg2', NewsMLG2Formatter(), 'NewsMLG2', ['wire'])
    app.download_formatter('json', JsonFormatter(), 'Json', ['agenda'])

    app.add_template_global(utils.get_picture, 'get_picture')
    app.add_template_global(utils.get_caption, 'get_caption')
    app.add_template_global(url_for_wire)
