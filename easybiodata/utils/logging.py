import datetime
import json
import logging
import logging.handlers
import os
import sys
import time
import flask
from werkzeug.exceptions import BadRequest


def setup_app_logging(app):
    del app.logger.handlers[:]

    _add_request_response_logging(app)
    _configure_root_logger_and_levels()


def log_exception_details(sender, exception):
    if isinstance(exception, BadRequest):
        sender.logger.info('Bad request details: {}'.format(exception.description))


def _add_request_response_logging(app):
    from flask import g, request
    from flask_login import current_user

    flask.got_request_exception.connect(log_exception_details)

    @app.before_request
    def log_before_request():
        if request.path == '/ping':
            return
        g.request_start = time.time()
        user = 'Anonymous' if current_user.is_anonymous else current_user.id
        app.logger.info('User {}: {} {}'.format(user, request.method, request.path))

    @app.after_request
    def log_after_request(response):
        if request.path == '/ping':
            return response
        duration = time.time() - g.request_start
        log_func = app.logger.info if duration < 5 else app.logger.warning
        user = 'Anonymous' if current_user.is_anonymous else current_user.id
        log_func('User {}: {} {} [{}] took {:.0f}ms'.format(user,
                                                            request.method,
                                                            request.path,
                                                            response.status_code, duration * 1000))
        return response


def setup_sqlalchemy_debug_logging(app):  # pragma: no cover
    if app.config['SQLALCHEMY_DEBUG']:
        import time
        from flask import request, g
        from sqlalchemy import event
        from easybiodata.core import db

        with app.app_context():
            @app.before_request
            def reset_counter():
                g.stmt_count = 0

            @app.after_request
            def print_counter(response):
                app.logger.debug('{} queries executed for endpoint {}'.format(g.stmt_count, request.endpoint))
                return response

            @event.listens_for(db.engine, 'after_cursor_execute')
            def log_statements(conn, cursor, statement, parameters, context, executemany):
                if hasattr(g, 'stmt_count'):
                    count = g.stmt_count
                    g.stmt_count += 1
                else:
                    count = '?'
                total = time.time() - conn.info['query_start_time'].pop()
                app.logger.debug(
                    '{} [{} - {:.2f}s] {} {}'.format(request.endpoint, count, total, statement, parameters))

            @event.listens_for(db.engine, 'before_cursor_execute')
            def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                conn.info.setdefault('query_start_time', []).append(time.time())


class JSONFormatter(logging.Formatter):
    def format(self, record):
        record.message = record.getMessage()
        if record.exc_info is not None:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        return self.formatMessage(record)

    def formatMessage(self, record):
        if record.exc_info is not None:
            exception_type = record.exc_info[0].__name__
        else:
            exception_type = None

        record_str = {'created'       : datetime.datetime.fromtimestamp(record.created,
                                                                        tz=datetime.timezone.utc).isoformat(),
                      'functionName'  : record.funcName,
                      'levelName'     : record.levelname,
                      'levelNo'       : record.levelno,
                      'loggerName'    : record.name,
                      'message'       : record.message,
                      'pathName'      : record.pathname,
                      'processId'     : record.process,
                      'exceptionType' : exception_type,
                      'traceback'     : record.exc_text}
        return 'easybiodata-api: {}'.format(json.dumps(record_str, separators=(',', ':')))


def _configure_root_logger_and_levels():
    root_logger = logging.getLogger()

    if os.getenv('easybiodata_CONFIG') == 'prod':
        handler = logging.handlers.SysLogHandler(('loggly', 514))
        handler.setLevel(logging.INFO)
        handler.setFormatter(JSONFormatter())
        root_logger.setLevel(logging.INFO)
    else:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [%(pathname)s:%(lineno)d]'))
        root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(handler)

    logging.getLogger('factory').setLevel(logging.WARN)
    logging.getLogger('alembic').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)
    logging.getLogger('newrelic').setLevel(logging.WARN)
    logging.getLogger('botocore').setLevel(logging.WARN)
    logging.getLogger('boto3').setLevel(logging.WARN)
