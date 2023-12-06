from django import forms

class SearchForm(forms.Form):
    '''
    Form that should be used to supply search criteria .
    At present, this is a generic form but in the future will be a model
    form, with the model recording all previous user searches.
    '''
    price_lims = (
        (50000, "£50,000"),
        (100000, "£100,000"),
        (200000, "£200,000"),
        (300000, "£300,000"),
        (400000, "£400,000"),
        (500000, "£500,000"),
        (600000, "£600,000"),
        (700000, "£700,000"),
        (800000, "£800,000"),
        (900000, "£900,000"),
        (1e16, "£1,000,000+"),
    )
    bedroom_choices_small = ((i, f"{i}") for i in range(1,8))
    bedroom_choices_big = ((i, f"{i}") for i in range(1,8))
    radii = ((rad*0.5, f"{rad*0.5:.2f} miles") for rad in range(6))

    postcode = forms.CharField(max_length=20)
    min_price = forms.ChoiceField(choices = price_lims)
    max_price = forms.ChoiceField(choices = price_lims)
    radius = forms.ChoiceField(choices = radii)

    min_bedrooms = forms.ChoiceField(choices = bedroom_choices_small)
    max_bedrooms = forms.ChoiceField(choices = bedroom_choices_big)

class URLForm(forms.Form):
    '''
    Form that lists the eligible search URLs.
    '''
    title = forms.CharField(max_length=255)
    search_url = forms.URLField()
