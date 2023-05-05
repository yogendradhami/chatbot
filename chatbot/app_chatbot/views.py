from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def Index(request):
    return HttpResponse("this is my first url.")

def Specific(request):
    return render(request, 'index.html')

# def Article(request,article_id):
#     return HttpResponse(article_id)