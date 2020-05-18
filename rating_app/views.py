import csv,io
from django.http import HttpResponse
from django.shortcuts import render,redirect
from rating_app.models import credited_courses_table,rating_table
from . import forms

def admin(request):
    template="admin.html"
    return render(request,template)

def database(request):
    template="database.html"
    return render(request,template)

def save_database(request):
    template="save_database.html"
    return render(request,template)

def evaluation_progress(request):
    if request.method=="GET":
        template="evaluation_progress.html"
        form=forms.progress()
        return render(request,template,{'form':form})
    else:
        form=forms.progress(request.POST)
        if form.is_valid():
            status=form.cleaned_data['Status']
            department=form.cleaned_data['Department']
            if credited_courses_table.objects.filter(feedback_status=status).exists() :
                q1 = credited_courses_table.objects.filter(roll_no__endswith=department)
                q2 = q1.filter(feedback_status=status).values('roll_no')
                return HttpResponse(q2)
            else :
                return HttpResponse('No matching rows')

def details(request):
    if request.method=="GET":
        template="details.html"
        form=forms.details()
        return render(request,template,{'form':form})
    else:
        form=forms.details(request.POST)
        if form.is_valid():
            a=form.cleaned_data['faculty_name']
            b=form.cleaned_data['course_name']
            if rating_table.objects.filter(faculty_name=a,course_name=b).exists() :
                abcd = rating_table.objects.get(faculty_name=a,course_name=b)
                ans=abcd.question_1+abcd.question_2+abcd.question_3+abcd.question_4+abcd.question_5+abcd.question_6+abcd.question_7
                ans=ans/7
                ans=ans/abcd.count
                perc=ans/5
                perc=perc*100
                text = str(perc) + "%"
                return render(request,'detailed_statistics.html',{'text':text,'abcd':abcd})
            else :
                return HttpResponse('Does not exist')

def overall(request):
    num1=0
    for a in rating_table.objects.all():
        num1=num1+a.count
    num2=0
    for b in credited_courses_table.objects.all():
        num2=num2+1
    num3=0
    for c in rating_table.objects.exclude(count=0):
        num3=num3+1
    num4=0
    for d in rating_table.objects.exclude(count=0):
        num4=num4+1
    num5=0
    for e in credited_courses_table.objects.filter(feedback_status=False):
        num5=num5+1
    return render(request,'overall_statistics.html',{'num1':num1,'num2':num2,'num3':num3,'num4':num4,'num5':num5})

def save_database_1(request):
    response1 = HttpResponse(content_type='text/csv')
    response1['Content-Disposition'] = 'attachment; filename="credited_courses_table.csv"'
    writer = csv.writer(response1)
    writer.writerow(['roll_no', 'faculty_name', 'course_name', 'feedback_status'])
    rows = credited_courses_table.objects.all()
    for row in rows:
        writer.writerow([row.roll_no,row.faculty_name,row.course_name,row.feedback_status])
    return response1

def save_database_2(request):
    response2 = HttpResponse(content_type='text/csv')
    response2['Content-Disposition'] = 'attachment; filename="rating_table.csv"'
    writer = csv.writer(response2)
    writer.writerow(['faculty_name', 'course_name', 'question_1', 'question_2', 'question_3', 'question_4', 'question_5', 'question_6', 'question_7', 'count'])
    rows = rating_table.objects.all()
    for row in rows:
        writer.writerow([row.faculty_name,row.course_name,row.question_1,row.question_2,row.question_3,row.question_4,row.question_5,row.question_6,row.question_7,row.count])
    return response2

def delete_database(request):
    credited_courses_table.objects.all().delete()
    rating_table.objects.all().delete()
    return HttpResponse('all tables cleared')

def update_database(request):
    template="update_database.html"
    prompt={
        'order' : 'Order of CSV file should be roll no., faculty name, course name.'
    }
    if request.method == "GET":
        return render(request,template,prompt)
    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'This is not a csv file')
    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        _, created = credited_courses_table.objects.update_or_create(
            roll_no=column[0],
            faculty_name=column[1],
            course_name=column[2],
            feedback_status = False
        )
        _, created = rating_table.objects.update_or_create(
            faculty_name=column[1],
            course_name=column[2],
            question_1 = 0,
            question_2 = 0,
            question_3 = 0,
            question_4 = 0,
            question_5 = 0,
            question_6 = 0,
            question_7 = 0,
            count = 0
        )
    context = {
    'order' : 'Successfully uploaded'
    }
    return HttpResponse('Successfully uploaded')
