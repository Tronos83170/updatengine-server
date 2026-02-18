###############################################################################
# UpdatEngine - Environment Variables Validation                               #
#                                                                             #
# Validates that all required environment variables / settings are present    #
# at Django startup. Raises ImproperlyConfigured with a clear message if not. #
###############################################################################

from django.core.exceptions import ImproperlyConfigured

# List of (setting_name, description) that must be non-empty at startup
REQUIRED_SETTINGS = [
    ("SECRET_KEY", "Django secret key (SECRET_KEY)"),
    ("ALLOWED_HOSTS", "List of allowed hosts (ALLOWED_HOSTS)"),
    ("DATABASES", "Database configuration (DATABASES)"),
]

# Required DB fields when using MySQL/MariaDB
REQUIRED_DB_FIELDS = ["NAME", "USER", "PASSWORD", "HOST"]


def check_required_settings(settings):
    """
    Call this from AppConfig.ready() or at the end of settings.py to validate
    that all critical settings are properly configured.

    Usage in an AppConfig:
        from updatengine.env_check import check_required_settings
        from django.conf import settings as django_settings
        check_required_settings(django_settings)
    """
    errors = []

    for setting_name, description in REQUIRED_SETTINGS:
        value = getattr(settings, setting_name, None)
        if not value:
            errors.append(f"  - Missing or empty: {description}")

    # Validate DB config for non-sqlite backends
    db_default = getattr(settings, "DATABASES", {}).get("default", {})
    engine = db_default.get("ENGINE", "")
    if "mysql" in engine or "postgresql" in engine:
        for field in REQUIRED_DB_FIELDS:
            if not db_default.get(field):
                errors.append(f"  - Missing DB setting: DATABASES['default']['{field}']")

    # Warn if DEBUG is True (should never be in production)
    if getattr(settings, "DEBUG", False):
        import warnings
        warnings.warn(
            "\n[UpdatEngine] WARNING: DEBUG=True is active. "
            "Never run with DEBUG=True in production!",
            RuntimeWarning,
            stacklevel=2,
        )

    # Warn if SECRET_KEY looks like a placeholder or default
    secret_key = getattr(settings, "SECRET_KEY", "")
    if secret_key and any(placeholder in secret_key for placeholder in ["changeme", "insecure", "${SECRET_KEY}", "your-secret"]):
        import warnings
        warnings.warn(
            "\n[UpdatEngine] WARNING: SECRET_KEY appears to be a placeholder value. "
            "Please generate a proper secret key.",
            RuntimeWarning,
            stacklevel=2,
        )

    if errors:
        raise ImproperlyConfigured(
            "\n[UpdatEngine] The following required settings are missing or invalid:\n"
            + "\n".join(errors)
            + "\n\nPlease check your .env file or environment variables."
        )
