from django.conf import settings
from django.template.loaders.filesystem import Loader
from django.template import Origin, TemplateDoesNotExist
from django.utils._os import safe_join
from base import utils

class ThemeLoader(Loader):

    def __init__(self, engine, theme_root = None):
        super().__init__(engine)
        self.theme_root = theme_root

    def get_template_sources(self, template_name):

        theme_dirs = [
            utils.CURRENT_THEME,
            'default'
        ]

        for template_dir in theme_dirs:
            # import pdb ; pdb.set_trace()
            try:
                name = safe_join(self.theme_root, template_dir, template_name)
            except Exception as e:
                # The joined path was located outside of this template_dir
                # (it might be inside another one, so this isn't fatal).
                continue

            yield Origin(
                name=name,
                template_name=template_name,
                loader=self,
            )