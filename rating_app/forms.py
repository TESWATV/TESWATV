from django import forms
from rating_app import models

star_choices=(
    (1 , '1' ),
    (2 , '2' ),
    (3 , '3' ),
    (4 , '4' ),
    (5 , '5' ),
)
status_choices=(
    (1,'Completed'),
    (0,'Pending'),
)
class evaluate_form(forms.Form):
    faculty_name=forms.ChoiceField()
    q1=forms.ChoiceField(choices=star_choices)
    q2=forms.ChoiceField(choices=star_choices)
    q3=forms.ChoiceField(choices=star_choices)
    def __init__(self,user_num,*args,**kwargs):
        super(evaluate_form,self).__init__(*args,**kwargs)
        self.fields['faculty_name']=forms.ChoiceField(choices=models.FeedbackTable.objects.filter(user_number=user_num,feedback=0).values_list('faculty_name','faculty_name'))

class log_in_class(forms.Form):
    user_name = forms.CharField(help_text='email')
    password = forms.CharField(help_text='password',widget=forms.PasswordInput)

class forgotpass(forms.Form):
    Email = forms.EmailField()
    user_id = forms.CharField()
    def __str__(self):
        return self.Email

class progress(forms.Form):
    Status = forms.ChoiceField(choices=status_choices)
    Department = forms.CharField()

class details(forms.Form):
    faculty_name = forms.CharField()
    course_name = forms.CharField()
