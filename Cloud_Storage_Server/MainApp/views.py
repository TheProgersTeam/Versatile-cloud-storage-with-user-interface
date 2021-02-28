from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework import status, generics
from rest_framework.views import APIView
from wsgiref.util import FileWrapper
from .serializers import *
from .models import *
from .forms import *
import os

DOMEN = "http://127.0.0.1:8000/"
# User authorization
def auth(token):
    try:
        token = Token.objects.get(key=token)
        user = User.objects.get(id=token.user_id)
        return "OK"
    except:
        return "ERR"

# file size
def file_size(path):
    return os.path.getsize(path)
# File path
def file_path(queryset):
    return queryset.file.path

''' Loading '''
class UploadFile(APIView): 
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            data = {"user": request.data.get("username"), "file": request.data.get("file")}
            file_serializer = FileSerializer(data=data)
            if file_serializer.is_valid(raise_exception=True):
                queryset = file_serializer.save()
                path = file_path(queryset) 
                size = file_size(path) 
                return Response({"data": {"id": queryset.id, "file": str(queryset.file), "dowload-link": DOMEN+"api/file/download/"+str(queryset.id)+"/", "info-link": DOMEN+"api/file/"+str(queryset.id)+"/", "delete-link": DOMEN+"api/file/delete/"+str(queryset.id)+"/", "user": queryset.user, "path": path, "size": size, "extension": queryset.extension, "image": str(queryset.image), "upload_date": queryset.upload_date}, "status": "OK"})
        else:
            return Response({"status": "ERR"})

''' Download '''
class DownloadFile(generics.ListAPIView):
    def get(self, request, pk, format=None):
        try:
            queryset = File.objects.get(id=pk) 
            path = queryset.file.path 
            response = FileResponse(open(path, 'rb')) 
            return response 
        except:
            return Response({"status": "ERR", 'message': 'File not found'})

''' Delete '''
class DeleteFile(generics.ListAPIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            try:
                queryset = File.objects.get(id=int(request.data.get("id"))) 
                if queryset.user == username:
                    queryset.delete()
                else:
                    return Response({"status": "ERR"})
            except:
                return Response({"status": "ERR"})

            return Response({"status": "OK", "message": "File deleted"})
        else:
            return Response({"status": "ERR"})

''' View '''
class ViewFile(APIView):
    def post(self, request, pk):
        try:
            queryset = File.objects.get(id=pk)
            path = file_path(queryset) 
            size = file_size(path) 
            return Response({"data": {"id": queryset.id, "file": str(queryset.file), "path": path, "size": size, "extension": queryset.extension, "image": str(queryset.image), "upload_date": queryset.upload_date}, "status": "OK"})
        except:
            return Response({"status": "ERR", 'error': 'File not found'})
    
''' View user's files '''
class ViewUserFiles(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            data = {}
            files = File.objects.filter(user=user)
            for i in files:
                data[str(i.file)] = {"id": i.id, "name": str(i.file), "extension": i.extension, "image": str(i.image), "upload_date": i.upload_date}

            return Response({"data": data, "status": "OK"})
        else:
            return Response({"status": "ERR"})
   
''' Checking your account for validity '''
class LoginView(APIView):
    permission_classes = ()

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            return Response({"status": "OK"})
        else:
            return Response({"status": "ERR"})

''' Registration '''
def RegPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save() 
            return redirect("home")

    context = {'title': 'Registration', 'form': form}
    return render(request, 'auth/reg.html', context)

''' Home page '''
def HomePage(request):
    context = {'title': 'Home'}
    return render(request, 'home/home.html', context)
