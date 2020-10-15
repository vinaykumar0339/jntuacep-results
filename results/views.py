from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from decimal import *
# Create your views here.

def home(request):
    return render(request,'index.html')

def result(request):
    roll_no = request.POST.get('roll_no')
    dob = request.POST.get('dob')
    sem = request.POST.get('semester')

    grades = {
        'S' : 10,
        'A++' : 9.5,
        'A+' : 9,
        'A' : 8.5,
        'B++' : 8,
        'B+' : 7.5,
        'B' : 7,
        'C++' : 6.5,
        'C+' : 6,
        'C' : 5.5,
        'D' : 5,
        'E' : 4.5,
        'F' : 0,
        'Ab' : 0
    }

    final_result = {}

    try:
        url = "https://jntuacep.ac.in/results/"+sem
        portal = requests.post(url,data={'roll_no':roll_no,'dob':dob})
        soup = BeautifulSoup(portal.content,'lxml')
        result = soup.find('section',{'id':"printResults"})
        # semester name
        semester = result.h6.text
        final_result['semester'] = semester

        # basic info
        basic_info = result.find_all('span')
        for index, tag in enumerate(basic_info):
            if (index == 1):
                final_result['hall_ticket'] = tag.b.text
            if (index == 3):
                final_result['student_name'] = tag.b.text
            if (index == 5):
                final_result['dob'] = tag.b.text

        # column names
        column = result.find_all('th')
        final_result['column_names'] = [] 
        for i in column:
            final_result['column_names'].append(i.text)

            
        # result data
        data = result.find('tbody').find_all('td')
        final_result['data'] = {}
        count = 1
        for i,d in enumerate(data):
            if i%6 == 0:
                sub = 'subject' + str(count)
                count = count + 1
                final_result['data'][sub] = []
            if '\r\n' in d.text or '\r' in d.text:
                final_result['data'][sub].append(d.text[0])
            else:
                final_result['data'][sub].append(d.text) 
        
        for sub in final_result['data']:
            score = final_result['data'][sub][4]
            final_result['data'][sub].append(grades[score])

        # total credits
        credits = []
        for sub in final_result['data']:
            credits.append(int(final_result['data'][sub][5]))


        # pass or fail 
        fail = 0
        absent = 0
        for sub in final_result['data']:
            f = final_result['data'][sub][3]
            ab = final_result['data'][sub][4]
            if f == 'F':
                fail += 1
            if ab == 'Ab':
                absent += 1

        final_result['fail'] = fail
        final_result['absent'] = absent

        sgpa = 0
        for sub in final_result['data']:
            sgpa += (float(final_result['data'][sub][5]) * float(final_result['data'][sub][6]))
            
        final_result['sgpa'] = Decimal(sgpa/sum(credits)).quantize(Decimal('.001'), rounding=ROUND_DOWN)
    except:
        pass
    print(final_result)
    return render(request,'result.html',context=final_result)