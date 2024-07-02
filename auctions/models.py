from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    pass

class Listing(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100,unique=True)
    image = models.ImageField(null=True, blank=True)
    desc = models.TextField()
    current_highest_bid = models.IntegerField(default=0)
    current_bidder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_bids')

    def update_current_bid(self, bidder):
        self.current_bidder = bidder
        self.save()

class Bid(models.Model):
    listing=models.ForeignKey(Listing,on_delete=models.CASCADE)
    bidder=models.ForeignKey(User,on_delete = models.CASCADE)
    bid_price = models.IntegerField()

    class Meta:
        unique_together = (('listing', 'bid_price'),)

class Comment(models.Model):
    listing = models.ForeignKey(Listing,on_delete=models.CASCADE,null=True,related_name='comments')
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    comment=models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.listing.name} at {self.timestamp}"