from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register)


from .models import SvgImage

""" Regestering SVG as model admin """
class MyPageModelAdmin(ModelAdmin):
    model = SvgImage
    menu_label = 'SVG Image'
    menu_icon  = 'image'
    list_display = ('image', 'title')

# Now you just need to register your customised ModelAdmin class with Wagtail
modeladmin_register(MyPageModelAdmin)