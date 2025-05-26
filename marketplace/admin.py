from django.contrib import admin
from .models import Farm, Product, ProductCategory, Order, OrderItem, Review, Profile

# Register Product with image preview
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'farm', 'price', 'stock', 'display_image')
    readonly_fields = ('display_image',)
    
    def display_image(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="150" height="150" style="object-fit: cover;">'
        return "No Image"
    display_image.allow_tags = True

# Register Farm with image preview
class FarmAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'display_image')
    readonly_fields = ('display_image',)
    
    def display_image(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="150" height="150" style="object-fit: cover;">'
        return "No Image"
    display_image.allow_tags = True

# Register all models
admin.site.register(Farm, FarmAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(Profile)