from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class ManifestStaticFilesStorageNotStrict(ManifestStaticFilesStorage):
    manifest_strict = False

    def url_converter(self, name, hashed_files, template=None):
        converter = super().url_converter(name, hashed_files, template)

        def safe_converter(matchobj):
            try:
                return converter(matchobj)
            except ValueError:
                return matchobj.group(0)

        return safe_converter
