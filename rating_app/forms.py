from django import forms
from rating_app import models

status_choices=(
    (1,'Completed'),
    (0,'Pending'),
)

class progress(forms.Form):
    Status = forms.ChoiceField(choices=status_choices)
    Roll_no_ends_with = forms.CharField(required=False)

class details(forms.Form):
    faculty_name = forms.CharField(required=False)
    course_name = forms.CharField(required=False)
