from easybiodata.core import db
from flask.ext.restful import Resource
from easybiodata.services import user_data


class Ping(Resource):
    def get(self):
        db.session.execute('SELECT 1')
        return {'pong': True, 
                'test': user_data.find(gender='female').first().first_name,
                'idea': user_data.find(caste='').first().first_name,
        }
