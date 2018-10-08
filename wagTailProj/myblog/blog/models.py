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



class BlogPage(Page):
    description = models.CharField(max_length=250, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('description', classname='full')
    ]

class PostPage(Page):
    body = RichTextField(blank=True)
    categories = ParentalManyToManyField('blog.BlogCatagory', blank=True)
    tags    = ClusterTaggableManager(through='blog.BlogPageTag', blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
        FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        FieldPanel('tags'),
    ]

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