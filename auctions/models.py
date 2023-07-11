from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    watchlist = models.ManyToManyField('AuctionListing', related_name='watchlist', blank=True)
    def __str__(self):
        return f'{self.id}. {self.username}'

class AuctionListing(models.Model):
    CATEGORY_CHOICES = [
        ('Other', 'Other'),
        ('Beauty', 'Beauty'),
        ('Fashion', 'Fashion'),
        ('Health', 'Health'),
        ('Home', 'Home'),
        ('Media', 'Media'),
        ('Sports', 'Sports'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, related_name='listing_user')
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=280)
    price = models.FloatField()
    photo = models.URLField(blank=True, default=None)
    category = models.CharField(max_length=64, choices=CATEGORY_CHOICES, default='Other')
    winner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None, blank=True, related_name='listing_winner')
    active = models.BooleanField(default=True)
    def __str__(self):
        return f'{self.id}. {self.title}: {self.description}, by {self.user.username}'
    
class AuctionComment(models.Model):
    item = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    text = models.CharField(max_length=280)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.id}. "{self.text}", by {self.user.username}'

class Bid(models.Model):
    item = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)    
    amount = models.FloatField()
    def __str__(self):
        return f'{self.id}. {self.amount}$, by {self.user.username}'