from django.http import HttpResponse
from pipes import Template
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, CreateView, ListView, DetailView
from .forms import *
from django.shortcuts import redirect
# Create your views here.
from .models import *
import pandas as pd
from os import remove
from project.models import Project
from django.db.models import Q, Count

# Create your views here.
import os.path

#Funciton that recieves the project id in order to delete all prototypes related to the project
def delete_prototypes(project_fields):
    project_prototypes = Prototype.objects.filter(project_field = project_fields)
    project_prototypes.delete()
    
#Function that recieves a list with all the rows from csv and the project field in order to register all the prototypes related
# to a projet
def save_data_csv(arr,project_field):
    equipments = Equipment.objects.all().order_by('id')
    iterable2 = 10
    iterable = 16
    helper = []
    helper2 = []
    project = Project.objects.get(id=project_field)
    for i in arr:
        if(i[8] == 'null'):
            segment = Segment.objects.get(name='No existe')    
        else:
            if(Segment.objects.filter(name=i[8]).exists() == False):
                segment = Segment.objects.get(name="No existe")
            else:
                segment = Segment.objects.get(name=i[8])
        
        if(i[9] == 'null'):
            property_type = PropertyType.objects.get(name='No existe')
        else:
            if(PropertyType.objects.filter(name=i[9]).exists() == False):
                property_type = PropertyType.objects.get(name='No existe')
            else:
                property_type = PropertyType.objects.get(name=i[9])
         
        for k in range(6):
            if(i[iterable2] == 'null'):
                finishing = Finishing.objects.get(name='No existe')
                helper.append(finishing)
                iterable2 = iterable2+1
            else:
                if(Finishing.objects.filter(name=i[iterable2]).exists() == False):
                    finishing = Finishing.objects.get(name='No existe')
                    helper.append(finishing)
                    iterable2 = iterable2+1
                else:
                    finishing = Finishing.objects.get(name=i[iterable2])
                    helper.append(finishing)
                    iterable2 = iterable2+1
        iterable2 = 10
        prototype = Prototype()
        prototype.segment_field = segment
        prototype.project_field = project
        prototype.name = i[0]
        prototype.price = i[1]
        prototype.total_units = i[2]
        prototype.sold_units = i[3]
        prototype.m2_terrain = i[4]
        prototype.m2_constructed = i[5]
        prototype.m2_habitable = i[6]
        prototype.propertyType = property_type
        prototype.save()
        prototype = Prototype.objects.get(name=i[0],project_field = project_field)
        prototype.finishings.set(helper)
        helper.clear()
        iterable = 16
        for equipment in equipments:
            if(i[iterable] == 'null' or i[iterable] == 0):
                equipment_quantity = EquipmentQuantity()
                equipment_quantity.equipment = equipment
                equipment_quantity.prototype = prototype
                equipment_quantity.quantity = 0
                equipment_quantity.save()
                iterable = iterable + 1
            else:
                equipment_quantity = EquipmentQuantity()
                equipment_quantity.equipment = equipment
                equipment_quantity.prototype = prototype
                equipment_quantity.quantity = i[iterable]
                equipment_quantity.save()
                iterable = iterable+1
        iterable = 16

#Function that saves and read the csv.
def handle_uploaded_file(f,project_field,action):  
    with open('static/'+f.name, 'wb+') as destination:  
        for chunk in f.chunks():  
            destination.write(chunk)
    valores = pd.read_csv('static/'+f.name)
    valores = valores.fillna("null")
    valores = valores.values.tolist()
    #That if compares if is to create prototyes or to update prototypes
    if(action=='c'):
        save_data_csv(valores,project_field)
    elif(action=='u'):
        delete_prototypes(project_field)
        save_data_csv(valores,project_field)
    remove('static/'+f.name)
#Class based view to create prototypes
class CreatePrototype(ListView):
    template_name = 'pages/form_prototype.html'
    model = Segment
    #Overwriting the method get from the class
    def get(self,request,*args,**kwargs):
        download_csv()
        return render(request,self.template_name,context={
            'list_segment':Segment.objects.all(),
            'id':self.kwargs['id']
            })
    #Overwriting the method post from the class
    def post(self,request,*args,**kwargs):
        csv_import = CSV_Form(request.POST, request.FILES)
        project_field = request.POST['project_field']
        if csv_import.is_valid():
                handle_uploaded_file(request.FILES['csv'],project_field,'c')
                return redirect("prototypes")
        else:
            return render(request,self.template_name,context={'Prueba':'No se pudo'})


class PrototypesListView(ListView):
    template_name = 'pages/prototypes.html'
    model = Prototype
    def get(self, request, *args,**kwargs):
        finishings_type = FinishingType.objects.exclude(name="No existe").order_by("id")
        return render(request,self.template_name,context={
            'prototype_list': Prototype.objects.all(),
            'finishings_type': finishings_type
        })

#Class based view to update prototype
class UpdatePrototype(ListView):
    template_name = 'pages/form_update_prototypes.html'
    model = Segment
    #Overwriting the method get from the class
    def get(self,request,*args,**kwargs):
        download_csv()
        return render(request,self.template_name,context={
            'id':self.kwargs['id']
            })
    #Overwriting the method post from the class
    def post(self,request,*args,**kwargs):
        csv_import = CSV_Form(request.POST, request.FILES)
        project_field = request.POST['project_field']
        if csv_import.is_valid():
                handle_uploaded_file(request.FILES['csv'],project_field,'u')
                return redirect("prototypes")
        else:
            return render(request,self.template_name,context={'Prueba':'No se pudo'})

#Function that create a csv with all the equipments from the database.
def download_csv():
    if(os.path.isfile("static/plantilla_prototipos2.csv")):
        remove("static/plantilla_prototipos2.csv")
    equipments = Equipment.objects.all().order_by('id')
    template = pd.read_csv("static/plantilla_prototipos.csv")
    arr = [""]
    for equipment in equipments:
        template[equipment.name] = arr
    template = template.drop(0)
    template.to_csv("static/plantilla_prototipos2.csv",sep=",",index=False,encoding="utf-8")
