easybiodata_MAX_NOTES_LENGTH = 1000
easybiodata_MAX_USERNAME_LENGTH = 15
easybiodata_MIN_PASSWORD_LENGTH = 5

easybiodata_EMAIL_REGEX = r'[^@]+@[^@]+\.[^@]+'
easybiodata_USERNAME_REGEX = r'[a-zA-Z0-9_]{1,%d}' % easybiodata_MAX_USERNAME_LENGTH
easybiodata_PASSWORD_REGEX = r'.{%d,}' % easybiodata_MIN_PASSWORD_LENGTH
