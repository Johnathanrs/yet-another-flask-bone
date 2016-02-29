# FREIGHTFLOW_MAX_ADDRESS_LENGTH = 100
# FREIGHTFLOW_MAX_DOT_NUMBER_LENGTH = 50
# FREIGHTFLOW_MAX_EMAIL_LENGTH = 100
# FREIGHTFLOW_MAX_HAPPENING_TYPE_LENGTH = 50
# FREIGHTFLOW_MAX_ID_LENGTH = 100
# FREIGHTFLOW_MAX_MC_NUMBER_COUNT = 100
# FREIGHTFLOW_MAX_MC_NUMBER_LENGTH = 100
# FREIGHTFLOW_MAX_NAME_LENGTH = 100
# FREIGHTFLOW_MAX_NOTES_LENGTH = 10000
# FREIGHTFLOW_MAX_PDF_HTML_LENGTH = 5 * 1024 * 1024
# FREIGHTFLOW_MAX_PARS_PAPS_COUNT = 100
# FREIGHTFLOW_MAX_PARS_PAPS_LENGTH = 100
# FREIGHTFLOW_MAX_TIMEZONE_LENGTH = 100
# FREIGHTFLOW_MAX_USERNAME_LENGTH = 15
# FREIGHTFLOW_MIN_PASSWORD_LENGTH = 8
# FREIGHTFLOW_MAX_LINE_ITEM_COUNT = 200

# FREIGHTFLOW_MAX_EXTERNAL_ID_COUNT = 200
# FREIGHTFLOW_MAX_EXTERNAL_ID_LENGTH = 200
# FREIGHTFLOW_MAX_EXTERNAL_ID_DESCRIPTION_LENGTH = 200

easybiodata_MAX_NOTES_LENGTH = 1000
easybiodata_MAX_USERNAME_LENGTH = 15
easybiodata_MIN_PASSWORD_LENGTH = 5

easybiodata_EMAIL_REGEX = r'[^@]+@[^@]+\.[^@]+'
easybiodata_USERNAME_REGEX = r'[a-zA-Z0-9_]{1,%d}' % easybiodata_MAX_USERNAME_LENGTH
easybiodata_PASSWORD_REGEX = r'.{%d,}' % easybiodata_MIN_PASSWORD_LENGTH
