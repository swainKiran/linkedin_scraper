from django.shortcuts import render

# Create your views here.


from django.shortcuts import render
from django.http import HttpResponse
from .models import MessageData
from .scraper import scrape_linkedin

def scrape_data(request):
    scrape_linkedin()
    return HttpResponse("Scraping initiated.")

def view_data(request):
    data = MessageData.objects.all()
    return render(request, 'scraper/view_data.html', {'data': data})
