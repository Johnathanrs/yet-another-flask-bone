#!/usr/bin/env python3

import importlib
import inspect
import pkgutil

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from flask.ext.migrate import Migrate, MigrateCommand, upgrade
from flask.ext.script import Shell, Manager, prompt_bool
from sqlalchemy import MetaData

from application import application as app
from easybiodata.core import db
import easybiodata
from easybiodata.users.models import UserData

manager = Manager(app)
migrate = Migrate(app, db)



admin = Admin(app, name='microblog', template_mode='bootstrap3')
admin.add_view(ModelView(UserData, db.session))


def _upgrade_database(revision='head'):
    app.logger.info('Creating db extensions')
    db.engine.execute('CREATE EXTENSION IF NOT EXISTS citext')
    if db.engine.scalar("SELECT 1 FROM pg_class WHERE relname = 'id_sequence'") is None:
        db.engine.execute('CREATE SEQUENCE id_sequence')

    app.logger.info('Running migrations')
    upgrade(revision=revision)


def _create_test_data():
    from easybiodata.utils.test_data import create_test_data

    app.logger.info('Creating test data')

    create_test_data()


@manager.option('-f', '--force', action='store_true', default=False, help="don't prompt before dropping tables")
@manager.option('-t', '--test_data', action='store_true', default=False, help='add test data to the database after recreating tables')
def recreate(force=False, test_data=False):
    """Drop tables and optionally add test data"""

    def drop_tables():
        m = MetaData()
        m.reflect(bind=db.engine)
        m.drop_all(bind=db.engine, tables=[t for t in m.sorted_tables if t.name != 'spatial_ref_sys'])
        db.engine.execute('DROP EXTENSION IF EXISTS citext')
        db.engine.execute('DROP SEQUENCE IF EXISTS id_sequence')

        db.engine.execute('DROP TABLE IF EXISTS alembic_version')

    force = force or prompt_bool('Are you sure you want to lose all your data?')
    if not force:
        app.logger.info('Not dropping tables')
        return
    app.logger.info('Dropping tables')
    drop_tables()

    # _upgrade_database(revision='147a0ce261c')

    # _upgrade_database(revision='b3a7c01729')

    # finish the upgrade to the most recent revision
    _upgrade_database()

    if test_data:
        _create_test_data()


@manager.command
def deploy_db():
    wipe = app.config['DEPLOYMENT_WIPE_DB']
    test_data = app.config['DEPLOYMENT_CREATE_TEST_DATA']
    if wipe:
        recreate(True, test_data)
    else:
        _upgrade_database()


def make_shell_context():
    def get_services():
        from easybiodata.core import Service

        context = {}
        m = importlib.import_module('easybiodata.services')
        for item_name in dir(m):
            item = getattr(m, item_name)
            if isinstance(item, Service):
                context[item_name] = item
        return context

    def get_schemas():
        from easybiodata.utils.schema import easybiodataSchema
        return _import_classes('{}.schemas', easybiodataSchema)

    context = dict(app=app, db=db,)
    context.update(get_model_context())
    context.update(get_services())
    context.update(get_schemas())
    return context


def _import_classes(module_pattern, klass):
    context = {}
    for _, modname, ispkg in pkgutil.walk_packages(easybiodata.__path__, prefix='easybiodata.'):
        try:
            if ispkg:
                m = importlib.import_module(module_pattern.format(modname))
                for item_name in dir(m):
                    item = getattr(m, item_name)
                    if inspect.isclass(item) and issubclass(item, klass):
                        context[item_name] = item
        except ImportError:
            pass
    return context


def get_model_context():
    return _import_classes('{}.models', db.Model)


if __name__ == '__main__':
    get_model_context()  # Make sure all models are referenced so they are included in migrations
    manager.add_default_commands()
    manager.add_command('shell', Shell(make_context=make_shell_context))
    manager.add_command('db', MigrateCommand)

    manager.run()
