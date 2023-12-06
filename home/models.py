from django.db import models

class URLs(models.Model):
	'''
	Creating ORM model for holding the result of a search of properties
	'''
	id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=255)
	search_url = models.URLField()
    
	def __str__(self):
		return self.title

	# Add metadata that is anything that is not a field. This might be more detailed information that we don't need in database
	class Meta():
		# ordering = ['-date_listed']
		# indexes = [models.Index(fields=["date_added_to_db"])]
		pass