from werkzeug.exceptions import ServiceUnavailable


class ExternalServiceError(ServiceUnavailable):
    message = description = 'There was a problem contacting an external service.'
