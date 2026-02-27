from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class ManifestStaticFilesStorageNotStrict(ManifestStaticFilesStorage):
    manifest_strict = False
