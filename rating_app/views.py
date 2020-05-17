import csv,io
from django.http import HttpResponse
from django.shortcuts import render,redirect
from rating_app.models import credited_courses_table,rating_table

# Create your views here.
# abcd
    'order' : 'Successfully uploaded'
    }
    return HttpResponse('Successfully uploaded')
    #return render(request,template,context)

def evaluation_progress(request):
    template="evaluation_progress.html"
