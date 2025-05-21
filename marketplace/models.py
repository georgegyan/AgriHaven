from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics', default='default.jpg')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'
class Farm(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='farm_images', default='default_farm.jpg')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class ProductCategory(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images', default='default_product.jpg')
    is_organic = models.BooleanField(default=False)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} from {self.farm.name}"

class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(default=timezone.now)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0)
    date_added = models.DateTimeField(default=timezone.now)

    @property
    def get_total(self):
        return self.product.price * self.quantity

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)