import datetime
from datetime import date
from django.db import models

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel

# New import added for Catagory -- register_snippet
from wagtail.snippets.models import register_snippet
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.tags import ClusterTaggableManager
from django import forms    

# New import added for Tagging -- TaggedItemBase, Tag as TaggitTag
from taggit.models import TaggedItemBase, Tag as TaggitTag

# New imprort for Routable page -- RoutablePageMixin, route, RoutablePageMixin, route
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtailmarkdown.fields import MarkdownField
from wagtailmarkdown.edit_handlers import MarkdownPanel



class BlogPage(RoutablePageMixin, Page):
    description = models.CharField(max_length=250, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('description', classname='full')
    ]

    def get_context(self, request, *args, **kwargs):
        context = super(BlogPage, self).get_context(request, *args, **kwargs)
        context['posts'] = self.posts
        context['blog_page'] = self
        return context

    def get_posts(self):
        return PostPage.objects.descendant_of(self).live()

    @route(r'^tag/(?P<tag>[-\w]+)/$')
    def post_by_tag(self, request, tag, *args, **kwargs):
        self.search_type = 'tag'
        self.search_term = tag
        self.posts       = self.get_posts().filter(tags__slug=tag)
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^tag/(?P<tag>[-\w]+)/$')
    def post_by_category(self, request, category, *args, **kwargs):
        self.search_type = 'category'
        self.search_type = category
        self.posts       = self.get_posts().filter(categories__slug=category)
        return Page.serve(self, request, *args, **kwargs)
    
    @route(r'^$')
    def post_list(self, request, *args, **kwargs):
        self.posts = self.get_posts()
        return Page.serve(self, request, *args, *kwargs)

class PostPage(Page):
    body = RichTextField(blank=True)
    date = models.DateTimeField("Post date", default=datetime.datetime.today)
    categories = ParentalManyToManyField('blog.BlogCatagory', blank=True)
    tags    = ClusterTaggableManager(through='blog.BlogPageTag', blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
        FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        FieldPanel('tags'),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('date')
    ]

    @property
    def blog_page(self):
        return self.get_parent().specific
    
    def get_context(self, request, *args, **kwargs):
        context = super(PostPage, self).get_context(request, *args, **kwargs)
        context['blog_page'] = self.blog_page
        return context

@register_snippet
class BlogCatagory(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, max_length=80)

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
        
    ]

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"  
    

class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('PostPage', related_name = 'post_tags')

@register_snippet
class Tag(TaggitTag):
    class Meta:
        proxy = True