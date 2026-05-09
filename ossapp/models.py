import datetime

from django.db import models

class Customer(models.Model):
    name=models.CharField(max_length=50)
    gender=models.CharField(max_length=6)
    address=models.TextField()
    pincode=models.IntegerField()
    contactno=models.CharField(max_length=15)
    emailaddress=models.EmailField(max_length=50,primary_key=True)
    password = models.CharField(max_length=20, null=True)
    regdate=models.DateTimeField(auto_now_add=True)

    def is_exists(self):
        if Customer.objects.filter(emailaddress=self.emailaddress):
            return True
        else:
            False

    @staticmethod
    def get_customer_by_email(email):
        return Customer.objects.get(emailaddress=email)



class Login(models.Model):
    userid=models.CharField(max_length=50,primary_key=True)
    password=models.CharField(max_length=20)
    usertype=models.CharField(max_length=30)

class Category(models.Model):
    name= models.CharField(max_length=50)
    def __str__(self):
        return self.name
    @staticmethod
    def get_all_category():
        return Category.objects.all()
    
class Owner(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    name= models.CharField(max_length=50)
    price= models.IntegerField(default=0)
    desc =models.CharField(max_length=200)
    category= models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    image= models.ImageField(upload_to='newproducts/')
    stock = models.IntegerField(default=0)

    @staticmethod
    def get_products_by_categoryid(category_id):
        return Product.objects.filter(category=category_id)


    @staticmethod
    def get_all_products():
        return Product.objects.all()
    @staticmethod
    def get_product_by_id(productid):
        return Product.objects.get(id=productid)


class Orders(models.Model):
    customer=models.ForeignKey(Customer,on_delete=models.DO_NOTHING)
    product=models.ForeignKey(Product,on_delete=models.DO_NOTHING)
    price=models.IntegerField()
    address=models.CharField(max_length=200)
    pincode=models.CharField(max_length=10)
    quantity= models.IntegerField()
    order_date=models.DateField(default=datetime.datetime.today)
    completed= models.BooleanField(default=False)
    customeremail=models.CharField(max_length=200)

class ShoppingCart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField()
    customeremail=models.CharField(max_length=200)

class DeliveryPerson(models.Model):
    first_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    city = models.CharField(max_length=100)  # New field for city
    collected_money = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # New field for money collected
    availability=models.IntegerField()
    password = models.CharField(max_length=128)


class MoneyCollection(models.Model):
    date = models.DateField()
    money_collected = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Money Collected on {self.date}: ${self.money_collected}"




class HealthCondition(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product2(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField()
    health_conditions = models.ManyToManyField(HealthCondition)

    def __str__(self):
        return self.name


class Review(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} - {self.product.name} - {self.rating} stars"


class Wishlist(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'product')

    def __str__(self):
        return f"{self.customer.name} - {self.product.name}"
    



    
