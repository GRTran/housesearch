from django import forms
from .models import Liked, Listing

class LikedForm(forms.ModelForm):
    '''
    Form that should be attached to listings view endpoint for the liked model
    '''
    class Meta:
        model = Liked
        fields = {'type' : 'L',
                  'type' : 'D'}