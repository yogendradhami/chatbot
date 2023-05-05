from django.shortcuts import render
from django.http import HttpResponse
from chatterbot import  ChatBot
from chatterbot.trainers import ListTrainer
# Create your views here.

def Index(request):
    return HttpResponse("this is my first url.")

def Specific(request):
    return render(request, 'index.html')

def getResponse(request):
    userMessage=request.GET.get('userMessage')
    return HttpResponse(userMessage)