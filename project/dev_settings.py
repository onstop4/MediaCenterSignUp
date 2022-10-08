from decouple import config

# Uses default settings for ALLOWED_HOSTS if variable is not set in .env file.
ALLOWED_HOSTS = (
    allowed_hosts_comma_separated.split(",")
    if (allowed_hosts_comma_separated := config("ALLOWED_HOSTS", default=""))
    else []
)

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
