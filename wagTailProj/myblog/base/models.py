from django.db import models
from wagtail.admin.edit_handlers import (FieldPanel, MultiFieldPanel,
                                         ObjectList,
                                         TabbedInterface)
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.core.fields import StreamField
from wagtail.images.edit_handlers import ImageChooserPanel

from wagtail.snippets.models import register_snippet
from django.conf import settings
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from modelcluster.fields import ParentalKey
from wagtailhyper.fields import HyperField, HyperFieldPanel
from wagtailhyper.models import WagtailHyperPage
from wagtail.search import index

AVIABLE_THEMES = getattr(settings, 'AVIABLE_THEMES', ['default'])

AVIABLE_THEMES = list(map(lambda x: (x, x), AVIABLE_THEMES))

CHANGE_FREQUENCY_CHOICES = [(item, item) for item in ["always", "hourly", "daily", "weekly", "monthly", "yearly", "never"]]

class Page(WagtailHyperPage):

    primary_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content = HyperField(blank=True, null=True, default="[]")

    og_title = models.CharField(max_length=255, blank=True, null=True)

    og_description = models.TextField(blank=True, null=True)

    og_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    select_template = models.CharField(max_length=255, blank=True, null=True)

    include_in_sitemap = models.BooleanField(default=True)
    priority = models.DecimalField(max_digits=4, decimal_places=2, default=0.8)
    changefreq = models.CharField(max_length=15, choices=CHANGE_FREQUENCY_CHOICES, default="daily")

    promote_panels = WagtailHyperPage.promote_panels + [
        MultiFieldPanel(
            [
                FieldPanel('og_title'),
                FieldPanel('og_description'),
                ImageChooserPanel('og_image'),
            ],
            heading = "Open Graph"
        )
    ]

    search_fields = WagtailHyperPage.search_fields + [ # Inherit search_fields from Page
        index.SearchField('content', partial_match=True),
        index.SearchField('search_description'),
    ]

    content_panels = WagtailHyperPage.content_panels + [
        ImageChooserPanel('primary_image'),
        HyperFieldPanel('content'),
    ]

    settings_panels = WagtailHyperPage.settings_panels + [
        FieldPanel('select_template'),
        MultiFieldPanel([
            FieldPanel('include_in_sitemap'),
            FieldPanel('priority'),
            FieldPanel('changefreq')
        ], heading='Sitemap Settings')
    ]

    class Meta:
        abstract = True

    def get_template(self, request, *args, **kwargs):
        templ = super(Page, self).get_template(request, *args, **kwargs)
        if self.select_template:
            return self.select_template
        return templ

    def get_sitemap_urls(self):
        if self.include_in_sitemap:
            return [
                {
                    'location': self.full_url,
                    'lastmod': (self.last_published_at or self.latest_revision_created_at),
                    'priority': "{:.1f}".format(self.priority),
                    'changefreq': self.changefreq
                }
            ]
        else:
            return []

class StandardPageTag(TaggedItemBase):
    content_object = ParentalKey('StandardBasePage', on_delete=models.CASCADE, related_name='tagged_items')

class StandardBasePage(Page):
    tags = ClusterTaggableManager(through=StandardPageTag, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('tags'),
    ]

@register_snippet
class BasicSnippet(models.Model):

    title = models.CharField(max_length=255)

    content = HyperField()

    panels = [
        FieldPanel('title'),
        HyperFieldPanel('content')
    ]

    def __str__(self):
        return self.title

@register_setting
class ApplicationSettings(BaseSetting):

    theme = models.CharField(help_text='Select which theme to use', max_length=255, choices=AVIABLE_THEMES, default='default')

    website_logo = models.ImageField(blank=True, null=True)

    website_favicon_icon = models.ImageField(blank=True, null=True)

    product_toolbar_base_url = models.URLField(blank=True, null=True)

    footer = models.ForeignKey(
        'base.BasicSnippet',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    header_top = models.ForeignKey(
        'base.BasicSnippet',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    footer_logo = models.ImageField(blank=True, null=True)

    google_analytics_key = models.CharField(max_length=255, blank=True, null=True)

    facebook_app_id = models.CharField(max_length=255, blank=True, null=True)
    facebook_admins = models.CharField(max_length=255, blank=True, null=True)

    open_graph_type = models.CharField(max_length=30, default="website", blank=True, null=True)

    facebook_url = models.URLField(help_text='Your Facebook page URL', blank=True, null=True)
    instagram_url = models.URLField(help_text='Your Instagram URL', blank=True, null=True)
    twitter_url = models.URLField(help_text='Your Twitter URL', blank=True, null=True)
    google_plus_url = models.URLField(help_text='Your google plus URL', blank=True, null=True)
    youtube_url = models.URLField(help_text='Your YouTube channel or user account URL', blank=True, null=True)
    linkedin_url = models.URLField(help_text='Your linkedin URL', blank=True, null=True)

    general_settings_panel = [
        FieldPanel('theme'),
        FieldPanel('website_logo'),
        FieldPanel('website_favicon_icon'),
        SnippetChooserPanel('header_top'),
        SnippetChooserPanel('footer'),
        FieldPanel('footer_logo'),
        FieldPanel('google_analytics_key'),
        FieldPanel('product_toolbar_base_url'),
    ]

    social_settings_panels = [
        MultiFieldPanel(
            [
                FieldPanel('facebook_url'),
                FieldPanel('instagram_url'),
                FieldPanel('twitter_url'),
                FieldPanel('google_plus_url'),
                FieldPanel('youtube_url'),
                FieldPanel('linkedin_url')
            ],
            heading='Social Links'
        ),
        MultiFieldPanel(
            [
                FieldPanel('facebook_app_id'),
                FieldPanel('facebook_admins'),
            ],
            heading='Facebook App'
        ),
        MultiFieldPanel(
            [
                FieldPanel('open_graph_type'),
            ],
            heading='Open Graph'
        ),
    ]

    edit_handler = TabbedInterface([
        ObjectList(general_settings_panel, heading='General'),
        ObjectList(social_settings_panels, heading='Social & SEO'),
    ])
