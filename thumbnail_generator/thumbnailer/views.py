import os

from celery import current_app
from django import forms
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from .tasks import gen_thumbnail

class FileUploadForm(forms.Form):
    file = forms.ImageField(required=True)

class HomeView(View):
    def get(self, request):
        form = FileUploadForm()
        return render(request, 'thumbnailer/home.html', {'form': form})

    def post(self, request):
        form = FileUploadForm(request.POST, request.FILES)
        context = {}

        if form.is_valid():
            file_path = os.path.join(settings.IMAGES_DIR, request.FILES['file'].name)
            with open(file_path, 'wb+') as file:
                for chunk in request.FILES['file'].chunks():
                    file.write(chunk)

            task = gen_thumbnail.delay(file_path, [(128, 128)])
            context['task_id'] = task.id
            context['task_status'] = task.status

            return render(request, 'thumbnailer/home.html', context)
        
        context['form'] = form
        print(context['form']['file'])
        return render(request, 'thumbnailer/home.html', context)

class TaskView(View):
    def get(self, request, task_id):
        task = current_app.AsyncResult(task_id)
        context = {
            'task_id': task_id,
            'task_status': task.status,
        }
        if task.status == 'SUCCESS':
            context['result'] = task.get()
        
        return JsonResponse(context)
        