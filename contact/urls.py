from django.urls import path, include
from .views import ContactListView, AddContactView, ContactDeleteView, ContactUpdateView, ContactViewSet, import_contacts
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'contacts', ContactViewSet, basename='api-contact')

app_name = 'contact'

urlpatterns = [
    path('', ContactListView.as_view(), name='contact-list'),
    path('add/', AddContactView.as_view(), name='contact-add'),
    path('delete/<int:pk>/', ContactDeleteView.as_view(), name='contact-delete'),
    path('edit/<int:pk>/', ContactUpdateView.as_view(), name='contact-edit'),
    path('import/', import_contacts, name='contact-import'),
    path('api/', include(router.urls)),
]