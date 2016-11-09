"""
Definition of models.
"""
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Shed(models.Model):
    zipcode = models.CharField(primary_key=True, max_length=5)
    name = models.CharField(max_length=20)
    address = models.CharField(max_length=20)


class UserProfile(models.Model):
    MALE = 'Male'
    FEMALE = 'Female'

    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )

    user_id = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    address = models.CharField(max_length=30)
    zipcode = models.ForeignKey(Shed)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=False, default=MALE)
    is_coordinator = models.BooleanField(default=0)


class Tool(models.Model):
    COMMON_USE = 'Common Use'
    GARDENING = 'Gardening'
    WOOD_WORKING = 'Wood Working'
    METAL_WORKING = 'Metal Working'
    CLEANING = 'Cleaning'
    KITCHEN = 'Kitchen'
    OTHERS = 'Others'

    CATEGORY_CHOICES = (
        (COMMON_USE, 'Common Use'),
        (GARDENING, 'Gardening'),
        (WOOD_WORKING, 'Wood Working'),
        (METAL_WORKING, 'Metal Working'),
        (CLEANING, 'Cleaning'),
        (KITCHEN, 'Kitchen'),
        (OTHERS, 'Others'),
    )

    ACTIVE = 'Active'
    INACTIVE = 'Inactive'

    ACTIVATION_STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    )

    NEW = 'New'
    LIKE_NEW = 'Like New'
    VERY_GOOD = 'Very Good'
    GOOD = 'Good'
    USABLE = 'Usable'

    CONDITION_CHOICES = (
        (NEW, 'New'),
        (LIKE_NEW, 'Like New'),
        (VERY_GOOD, 'Very Good'),
        (GOOD, 'Good'),
        (USABLE, 'Usable'),
    )

    HOME = 'Home'
    SHED = 'Shed'

    LOCATION = (
        (HOME, 'Home'),
        (SHED, 'Shed'),
    )

    tool_name = models.CharField(max_length=20)
    location = models.CharField(max_length=4, choices=LOCATION,blank=False, default='Home')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES,blank=False, default='New')
    status = models.CharField(max_length=20, choices=ACTIVATION_STATUS_CHOICES,blank=False, default='Active')
    tool_owner_id = models.ForeignKey(User)
    registration_date = models.DateField(default=datetime.now, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES,blank=False, default='Common Use')
    special_instruction = models.TextField(blank=True, null=True)
    image = models.FileField(upload_to='tool', blank=True, null=True)
    is_borrowed = models.BooleanField(default=False)
    share_zone = models.ForeignKey(Shed)


class ActiveTransactions(models.Model):
    tool = models.ForeignKey(Tool)
    borrower_id = models.ForeignKey(User, related_name='borrower_id')
    borrower_message = models.CharField(max_length=256, blank=True)
    owner_id = models.ForeignKey(User, related_name='owner_id')
    return_date = models.DateField(null=False)
    is_request_approved = models.BooleanField(default=False, blank=True)
    is_set_for_return = models.BooleanField(default=False)
    

class ToolHistory(models.Model):

    BORROWED = 'Borrowed'
    RETURNED = 'Returned'

    TRANSACTION_TYPE_CHOICES = (
        (BORROWED, 'Borrowed'),
        (RETURNED, 'Returned'),
    )

    NEW = 'New'
    LIKE_NEW = 'Like New'
    VERY_GOOD = 'Very Good'
    GOOD = 'Good'
    USABLE = 'Usable'

    CONDITION_CHOICES = (
        (NEW, 'New'),
        (LIKE_NEW, 'Like New'),
        (VERY_GOOD, 'Very Good'),
        (GOOD, 'Good'),
        (USABLE, 'Usable'),
    )

    tool_id = models.ForeignKey(Tool)
    borrower_id = models.ForeignKey(User, related_name='borrower_id_history')
    owner_id = models.ForeignKey(User, related_name='owner_id_history')
    transaction_date = models.DateField(null=False)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    owner_comments = models.CharField(max_length=100, blank=True)
    borrower_message = models.CharField(max_length=256, blank=True)
    return_date = models.DateField()
    #request_status = models.BooleanField(default=False) #holds true if request has been acceptec otherwirse False.


class Notification(models.Model):
    code = models.CharField(unique=True, max_length=5)
    type = models.CharField(max_length=25)
    description = models.CharField(max_length=256, blank=True)


class Notification_User(models.Model):
    notification = models.ForeignKey(Notification)
    user = models.ForeignKey(User)
    isSeen = models.BooleanField(default=False)
    tool_name = models.ForeignKey(Tool,null=True)
    description = models.CharField(max_length=128, blank=True)



