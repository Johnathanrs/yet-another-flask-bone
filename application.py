import os

config_name = os.environ.get('easybiodata_CONFIG', 'local')

import easybiodata
application = easybiodata.create_app(config_name)
