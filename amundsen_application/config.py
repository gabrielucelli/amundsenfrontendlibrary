import os
from typing import Any, Tuple
from typing import Callable, Dict, Optional, Set  # noqa: F401
from amundsen_application.models.user import User

from flask import Flask  # noqa: F401

from amundsen_application.tests.test_utils import get_test_user

from flaskoidc.config import BaseConfig

import logging

LOGGER = logging.getLogger(__name__)


class Config(BaseConfig):
    LOG_FORMAT = '%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s.%(funcName)s:%(lineno)d (%(process)d:' \
                 + '%(threadName)s) - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
    LOG_LEVEL = 'INFO'

    # Path to the logging configuration file to be used by `fileConfig()` method
    # https://docs.python.org/3.7/library/logging.config.html#logging.config.fileConfig
    # LOG_CONFIG_FILE = 'amundsen_application/logging.conf'
    LOG_CONFIG_FILE = None

    COLUMN_STAT_ORDER = None  # type: Dict[str, int]

    UNEDITABLE_SCHEMAS = set()  # type: Set[str]

    # Number of popular tables to be displayed on the index/search page
    POPULAR_TABLE_COUNT = 4  # type: int

    # Request Timeout Configurations in Seconds
    REQUEST_SESSION_TIMEOUT_SEC = 3

    # Mail Client Features
    MAIL_CLIENT = None
    NOTIFICATIONS_ENABLED = False

    # Flask `SECRET_KEY` config value
    FLASK_OIDC_SECRET_KEY: 'base-flask-oidc-secret-key'

    # Comma separated string of URLs which should be exposed without authentication, else all request will be authenticated.
    FLASK_OIDC_WHITELISTED_ENDPOINTS: "healthcheck"

    # Path of your configuration file. (default value assumes you have a `config/client_secrets.json` available.
    FLASK_OIDC_CLIENT_SECRETS: 'config/client_secrets.json'

    # Details about this below in the "Session Management" section.
    FLASK_OIDC_SQLALCHEMY_DATABASE_URI: 'postgresql://amundsen:amundsen@db.amundsensession.dev:5432/amundsen'


def private(app):
    return str(app.oidc.user_getfield('email'))

def logout(app):
    app.oidc.logout()
    return 'Hi, you have been logged out! <a href="/">Return</a>'

def custom_routes(app: Flask) -> Any:
    app.add_url_rule('/private', 'private', lambda : private(app))
    app.add_url_rule('/logout2', 'logout2', lambda : logout(app))

def get_access_headers(app):
    """
    Function to retrieve and format the Authorization Headers
    that can be passed to various microservices who are expecting that.
    :param oidc: OIDC object having authorization information
    :return: A formatted dictionary containing access token
    as Authorization header.
    """

    try:
        access_token = app.oidc.get_access_token()
        return {'Authorization': 'Bearer {}'.format(access_token)}
    except Exception:
        return None

def get_auth_user(app):
    """
    Retrieves the user information from oidc token, and then makes
    a dictionary 'UserInfo' from the token information dictionary.
    We need to convert it to a class in order to use the information
    in the rest of the Amundsen application.
    :param app: The instance of the current app.
    :return: A class UserInfo
    """

    from flask import g
    user_info = type('UserInfo', (object,), g.oidc_id_token)

    # noinspection PyUnresolvedReferences
    user_info.user_id = user_info.email
    return user_info

class LocalConfig(Config):
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'DEBUG'

    FRONTEND_PORT = '5000'
    # If installing locally directly from the github source
    # modify these ports if necessary to point to you local search and metadata services
    SEARCH_PORT = '5001'
    METADATA_PORT = '5002'

    # If installing using the Docker bootstrap, this should be modified to the docker host ip.
    LOCAL_HOST = '0.0.0.0'

    FRONTEND_BASE = os.environ.get('FRONTEND_BASE',
                                   'http://{LOCAL_HOST}:{PORT}'.format(
                                       LOCAL_HOST=LOCAL_HOST,
                                       PORT=FRONTEND_PORT)
                                   )

    SEARCHSERVICE_REQUEST_CLIENT = None
    SEARCHSERVICE_REQUEST_HEADERS = None
    SEARCHSERVICE_BASE = os.environ.get('SEARCHSERVICE_BASE',
                                        'http://{LOCAL_HOST}:{PORT}'.format(
                                            LOCAL_HOST=LOCAL_HOST,
                                            PORT=SEARCH_PORT)
                                        )

    METADATASERVICE_REQUEST_CLIENT = None
    METADATASERVICE_REQUEST_HEADERS = None
    METADATASERVICE_BASE = os.environ.get('METADATASERVICE_BASE',
                                          'http://{LOCAL_HOST}:{PORT}'.format(
                                              LOCAL_HOST=LOCAL_HOST,
                                              PORT=METADATA_PORT)
                                          )

    # If specified, will be used to generate headers for service-to-service communication
    # Please note that if specified, this will ignore following config properties:
    # 1. METADATASERVICE_REQUEST_HEADERS
    # 2. SEARCHSERVICE_REQUEST_HEADERS
    
    REQUEST_HEADERS_METHOD = get_access_headers

    AUTH_USER_METHOD = get_auth_user
    GET_PROFILE_URL = None

     # Initialize custom routes
    INIT_CUSTOM_ROUTES = custom_routes  # type: Callable[[Flask], None]


class TestConfig(LocalConfig):
    AUTH_USER_METHOD = get_test_user
    NOTIFICATIONS_ENABLED = True


class TestNotificationsDisabledConfig(LocalConfig):
    AUTH_USER_METHOD = get_test_user
    NOTIFICATIONS_ENABLED = False
