import datetime
from datetime import date
from django.db import models

from django import forms
from django.core.exceptions import ValidationError
import xml.etree.cElementTree as et


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

# New import for image 
from wagtail.core.models import Page, Orderable
from wagtail.images.edit_handlers import ImageChooserPanel
from django.utils.html import format_html


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

#################################################################################

# class SVGAndImageField(models.ImageField):
#     def formfield(self, **kwargs):
#         defaults = {'form_class': SVGAndImageFieldForm}
#         defaults.update(kwargs)
#         return super().formfield(**defaults)

# class SVGAndImageFieldForm(forms.ImageField):
#     def to_python(self, data):
#         try:
#             f = super().to_python(data)
#         except ValidationError:
#             return validate_svg(data)

#         return f


def validate_svg(f):
    # Find "start" word in file and get "tag" from there
    f.seek(0)
    tag = None
    try:
        for event, el in et.iterparse(f, ('start',)):
            tag = el.tag
            break
    except et.ParseError:
        pass

    # Check that this "tag" is correct
    if tag != '{http://www.w3.org/2000/svg}svg':
        raise ValidationError('Uploaded file is not an image or SVG file.')

    # Do not forget to "reset" file
    f.seek(0)

    return f



class SvgImage(models.Model):
    title = models.CharField(max_length=250)
    image = models.FileField(null=True, blank=True, validators=[validate_svg])

    def colored_name(self):
        return format_html(
            '<img src="{}" alt="{}" height="87px" width="100px" />',
            self.image,
            self.title,
        )

    panels = [
        FieldPanel('title'),
        FieldPanel('image')
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "SvgImage"
        verbose_name_plural = "Svg Images" 




