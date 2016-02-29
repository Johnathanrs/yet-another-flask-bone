from flask import request, g
from flask_login import current_user, login_required

from easybiodata.services import files, images
from easybiodata.images.v1.schemas import ImagesRequestSchema, ImageFilesResponseSchema, AllImagesResponseSchema, ImageResponseSchema

from easybiodata.utils.decorators import with_response_schema, with_request_schema
from flask.ext.restful import Resource


class Images(Resource):
    method_decorators = [login_required]

    @with_request_schema(ImagesRequestSchema())
    @with_response_schema(ImageResponseSchema())
    def put(self):
        myimage = images.create(creator=current_user,
                                **g.deserialized)
        return myimage

    @with_response_schema(AllImagesResponseSchema())
    def get(self):
        image = images.all()
        return image


class Image(Resource):
    method_decorators = [login_required]

    @with_response_schema(ImageResponseSchema())
    def get(self, image_id):
        myimage = images.get(image_id)
        return myimage


class ImageUpload(Resource):
    method_decorators = [login_required]

    @with_response_schema(ImageFilesResponseSchema())
    def put(self):
        image = images.upload_image_with_boto(request, current_user)
        return image
