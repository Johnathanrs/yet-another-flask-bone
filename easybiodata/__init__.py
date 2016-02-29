import inspect

from flask.ext.login import LoginManager
from flask.ext.restful import Api


def _generate_errors():
    import easybiodata.errors
    exceptions = {name: {'message': cls.description,
                         'status' : cls.code}
                  for name, cls in inspect.getmembers(easybiodata.errors, inspect.isclass)}
    return exceptions


login_manager = LoginManager()
api = Api(catch_all_404s=True, errors=_generate_errors())


def create_app(config_name):
    from easybiodata import factory
    app = factory.create_app(__name__, config_name)

    _register_routes()

    api.init_app(app)
    login_manager.init_app(app)
    return app


def _register_routes():
    from easybiodata import routes
    routes.add_routes(api)
