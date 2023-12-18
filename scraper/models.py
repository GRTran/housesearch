from django.db import models
from django.utils import timezone
from home.models import ReferenceURLs

class Listing(models.Model):
	'''
	Creating ORM model for holding the result of a search of properties
	'''
	id = models.BigIntegerField(primary_key=True)
	title = models.CharField(max_length=255)
	description = models.CharField(max_length=10000)
	region_id = models.CharField(max_length=255, null = True)
	price = models.IntegerField()
	url = models.URLField()
	image_url = models.URLField()
	num_images = models.IntegerField(default = 0)
	reduced = models.BooleanField(default = False)
	date_listed = models.DateField(default = timezone.now, null = True)
	date_added_to_db = models.DateField(default = timezone.now)
	liked = models.IntegerField(default = 0)
	referenceurls = models.ManyToManyField(ReferenceURLs)
    
	def __str__(self):
		return self.title

	# Add metadata that is anything that is not a field. This might be more detailed information that we don't need in database
	class Meta():
		# ordering = ['-date_listed']
		# indexes = [models.Index(fields=["date_added_to_db"])]
		pass
    
class Liked(models.Model):
	'''
	Create an additional model that has a foreign key which is the Listing that was liked or disliked
	'''
	FEEDBACK_OPTIONS = ( ('L', 'Like'),
		('D', 'Dislike'))
	type = models.CharField(max_length=1, choices=FEEDBACK_OPTIONS)
	user_response = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='user_response')

class SearchedListings(models.Model):
	id = models.BigIntegerField(primary_key=True)
	page = models.IntegerField()
	hashref = models.CharField(max_length=255, null = True)