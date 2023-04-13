from django.db import models
from django.utils import timezone

from datetime import datetime
from random import random 

# Create a model that is a singular listing
class Listing(models.Model):
    # Create a listing that has all of the information for a given listing.
	# This information will be stored in a database so that it can be easily retrieved later
	# Will also allow for cross-comparisons of listings so that they are not duplicated
	# id = models.Index()

	# Listing information
	title = models.CharField(name = "title", default = "", max_length=200)
	date_listed = models.DateField(name="date_listed", default=timezone.now)
	date_added_to_db = models.DateField(name="date_added_to_db", default=timezone.now)
	url = models.URLField(name="url", default="", max_length=200)
	city = models.CharField(name="city", default="", blank=True, max_length=200)
	county = models.CharField(name="county", default="", blank=True, max_length=200)
	image_url = models.URLField(name="image_url", default="", max_length=400)

	def __str__(self):
		return self.title



	# Add metadata that is anything that is not a field. This might be more detailed information that we don't need in database
	class Meta():
		ordering = ['-date_listed']
		indexes = [models.Index(fields=["date_added_to_db"])]
		pass