from django.shortcuts import render
from django.http import HttpResponse
from chatterbot import  ChatBot
from chatterbot.trainers import ListTrainer,chatterBotCorpusTrainer
# Create your views here.

bot = ChatBot('chatbot', read_only= False,
              logic_adapters=[
                  {
                  'import_path':'chatterbot.logic.BestMatch'
                #   'default_response':"Sorry, I don't know what that means.",
                #   'maximum_similarity_threshold':0.95,
                  }])

list_to_train=[
    "hi", # question
    "hi, there", # answer
    "what's your name?", #
    "I'm just a chatbot",
    "What is your favourite food ?",
    "I like cheese",
    "What's your favourite sport?",
    "swimming",
    "do you have children?",
    "no"
]

chatterbotCorpusTrainer = chatterBotCorpusTrainer(bot)

# list_tainer = ListTrainer(bot)
# list_tainer.train(list_to_train)
chatterbotCorpusTrainer.train('chatterbot.corpus.english')


def Index(request):
    return HttpResponse("this is my first url.")

def Specific(request):
    return render(request, 'index.html')

def getResponse(request):
    userMessage=request.GET.get('userMessage')
    chatResponse=str(bot.get_response(userMessage))
    return HttpResponse(chatResponse)