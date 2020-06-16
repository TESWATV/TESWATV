from django import forms
from rating_app import models

status_choices=(
    (1,'Completed'),
    (0,'Pending'),
)

class progress(forms.Form):
    Status = forms.ChoiceField(choices=status_choices)
    Roll_no_ends_with = forms.CharField()

class details(forms.Form):
    faculty_name = forms.CharField()
    course_name = forms.CharField()
