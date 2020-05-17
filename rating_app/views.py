import csv,io
from django.http import HttpResponse
from django.shortcuts import render,redirect
from rating_app.models import credited_courses_table,rating_table

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
    #return render(request,template,context)

def evaluation_progress(request):
    template="evaluation_progress.html"
