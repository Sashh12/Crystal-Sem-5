from django.db import models
from django.contrib.auth.models import User

# Create your models here.
STATE_CHOICES = (
    ('Andaman and Nicobar Islands','Andaman and Nicobar Islands'),
    ('Andhra Pradesh','Andhra Pradesh'),
    ('Arunachal Pradesh','Arunachal Pradesh'),
    ('Assam','Assam'),
    ('Bihar','Bihar'),
    ('Chandigarh','Chandigarh'),
    ('Chhattisgarh','Chhattisgarh'),
    ('Daman and Diu','Daman and Diu'),
    ('Dadra and Nagar Haveli','Dadra and Nagar Haveli'),
    ('Delhi','Delhi'),
    ('Goa','Goa'),
    ('Gujarat','Gujarat'),
    ('Haryana','Haryana'),
    ('Himachal Pradesh','Himachal Pradesh'),
    ('Jammu and Kashmir','Jammu and Kashmir'),
    ('Jharkhand','Jharkhand'),
    ('Karnataka','Karnataka'),
    ('Kerala','Kerala'),
    ('Lakshadweep','Lakshadweep'),
    ('Madhya Pradesh','Madhya Pradesh'),
    ('Maharashtra','Maharashtra'),
    ('Manipur','Manipur'),
    ('Mizoram','Mizoram'),
    ('Meghalaya','Meghalaya'),
    ('Nagaland','Nagaland'),
    ('Odisha','Odisha'),
    ('Puducherry','Puducherry'),
    ('Punjab','Punjab'),
    ('Rajasthan','Rajasthan'),
    ('Sikkim','Sikkim'),
    ('Tamil Nadu','Tamil Nadu'),
    ('Telangana','Telangana'),
    ('Tripura','Tripura'),
    ('Uttar Pradesh','Uttar Pradesh'),
    ('Uttarakhand','Uttarakhand'),
    ('West Bengal','West Bengal'),
)

CATEGORY_CHOICES=(
    ('BR','Braclet'),
    ('NL','Neckpiece'),
    ('RG','Ring'),
    ('EG','Earrings'),
    ('EX','Exclusive'),
    ('CH','GuaSha'),
    ('AN','Anxiety'),
    ('DP','Depression'),
    ('HP','Happiness'),
    ('NG','Negativity'),
    ('PC','Peace'),
    ('MT','Motivation'),
    ('RD','Red'),
    ('MC','Multicolour'),
    ('GE','Green'),
    ('BL','Blue'),
    ('PK','Pink'),
    ('PL','Purple'),
    ('AT','Amazonite'),
    ('','Aquamarine'),
    ('','Blue Gold Stone'),
    ('','Golden Quartz'),
    ('','Green Fluorite'),
    ('JP','Jasper'),
    ('','Garnet'),
    ('ML','Malachite'),
    ('OP','Opalite'),
    ('RQ','Rose Quartz'),
    ('SE','Selenite'),
    ('','Green Jade'),
    ('RH','Rhodonite'),
    ('','Pyrite'),
    ('','Strawberry Quartz'),
    ('',''),
    ('',''),
    ('',''),
    ('',''),
)


class Product(models.Model):
    title = models.CharField(max_length=100)
    selling_price = models.FloatField()
    discounted_price = models.FloatField()
    description = models.TextField()
    #context = models.TextField(default=' ')
    customization = models.TextField(default=' Not Available')
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    #category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    product_image = models.ImageField(upload_to='product')
    def __str__(self):
        return self.title 
    
class Customer(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    village = models.CharField(max_length=200)
    landmark = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    mobile = models.IntegerField(default=0,help_text = "Please enter 10 digits valid Number")
    pincode = models.IntegerField()
    state = models.CharField(choices=STATE_CHOICES,max_length=100)
    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
       
    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price


STATUS_CHOICES = (
    ('Accepted','Accepted'),
    ('Packed','Packed'),
    ('On The Way','On The Way'),
    ('Delivered','Delivered'),
    ('Cancel','Cancel'),
    ('Pending','Pending'),
)

class Payment(models.Model):
    user =  models.ForeignKey(User,on_delete=models.CASCADE)
    amount = models.FloatField()
    razorpay_order_id = models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_status = models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_id = models.CharField(max_length=100,blank=True,null=True)
    paid = models.BooleanField(default=False)

class OrderPlaced(models.Model):
    user =  models.ForeignKey(User,on_delete=models.CASCADE)
    customer =  models.ForeignKey(Customer,on_delete=models.CASCADE)
    product =  models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status =  models.CharField(max_length=50,choices=STATUS_CHOICES, default='Pending')
    payment = models.ForeignKey(Payment,on_delete=models.CASCADE,default="")
    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price
    
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

class Feedback(models.Model):
    name=models.CharField(max_length=200)
    email=models.EmailField()
    comment=models.TextField()
    def __str__(self):
        return self.name