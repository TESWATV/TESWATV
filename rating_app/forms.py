from django import forms
star_choices=[
    ('1' , '1' ),
    ('2' , '2' ),
    ('3' , '3' ),
    ('4' , '4' ),
    ('5' , '5' ),
]

class rate_form(forms.Form):
    q1 = forms.ChoiceField(choices=star_choices,widget=forms.RadioSelect)
    q2 = forms.ChoiceField(choices=star_choices,widget=forms.RadioSelect)
