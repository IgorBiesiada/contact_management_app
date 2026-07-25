from django.shortcuts import redirect, render
from django.views.generic import ListView, UpdateView, DeleteView, CreateView
from .models import Contact, ContactStatusChoices
from .forms import ContactForm
from django.urls import reverse_lazy
from .services import get_weather_for_city
from rest_framework import viewsets
from .serializers import ContactSerializer, ContactDetailSerializer
import csv
from django.contrib import messages
from django.db.models import Q
from django.db import transaction
# Create your views here.

class AddContactView(CreateView):
    model = Contact
    template_name = 'add.html'
    context_object_name = 'contact'
    form_class = ContactForm
    success_url = '/'

class ContactListView(ListView):
    model = Contact
    template_name = 'list.html'
    context_object_name = 'contacts'

    def get_queryset(self):
        #using select_related to prevent the N+1 database queries problem for the 'status' foreign key
        queryset = Contact.objects.select_related('status')
        search_query = self.request.GET.get('q')
        sort_by = self.request.GET.get('sort')

        # global search across multiple fields
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone_number__icontains=search_query) |
                Q(city_of_residence__icontains=search_query)
            )

        #validate sort parameter to prevent FieldError / SQL Injection
        if sort_by in ['last_name', 'date', '-date']:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        """
        Fetch weather data for each contact 
        Performance is maintained because get_weather_for_city utilizes a 30-minute cache
        preventing an N+1 API call issue here
        """
        for contact in context['object_list']:
            if contact.city_of_residence: 
                contact.weather = get_weather_for_city(contact.city_of_residence)
            else:
                contact.weather = None
        return context

class ContactUpdateView(UpdateView):
    model = Contact
    template_name = 'edit.html'
    context_object_name = 'contact'
    form_class = ContactForm
    success_url = '/'

class ContactDeleteView(DeleteView):
    model = Contact
    template_name = 'delete.html'
    success_url = reverse_lazy('contact:contact-list')

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ContactSerializer
        return ContactDetailSerializer


@transaction.atomic
def import_contacts(request):
    """
    Handles CSV file upload and imports contacts into the database.
        Wrapped in transaction.atomic() to ensure an all-or-nothing approach. 
        If the import fails at any point, no partial data is saved.
    """

    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
            
        if csv_file:
            #using decode with utf-8 for on-the-fly conversion
            file_data = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(file_data)
                
            for row in reader:
                email = row.get('email', '')
                phone_number = row.get('phone', '')

                # if statment for catching duplicate data
                if Contact.objects.filter( Q(email=email) | Q(phone_number=phone_number)).exists():
                    continue
                    
                status = row.get('status', '').strip()
                #if the status is not specified in the CSV file, we paste it in "nowy"
                if not status:
                    status = 'nowy'

                #using get_or_create for prevents a situation where someone enters a status in the CSV file that does not yet exist in the database
                status_obj = ContactStatusChoices.objects.get_or_create(name=status)[0] #[0] because we need to unpack the tuple
                Contact.objects.create(
                    first_name=row.get('first_name', ''),
                    last_name=row.get('last_name', ''),
                    email=email,
                    phone_number=phone_number,
                    city_of_residence=row.get('city_of_residence', ''),
                    status=status_obj
                )
        return redirect('contact:contact-list')
            
    return render(request, 'import.html')