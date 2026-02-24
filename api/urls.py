from django.urls import path
from . import views

urlpatterns = [
    # Page Routes
    path('', views.home_page, name='home'),
    path('prescription/', views.prescription_page, name='prescription'),
    path('lab-buddy/', views.lab_page, name='lab_buddy'),
    path('grandma/', views.grandma_page, name='grandma'),

    # --- NEW PHYSICIAN HUB PAGE ROUTES ---
    path('soap/', views.soap_page, name='soap_page'),
    path('network/', views.network_page, name='network_page'),
    path('logic/', views.logic_page, name='logic_page'),

    # API Endpoints
    path('api/analyze/', views.analyze_prescription, name='analyze_prescription'),
    path('api/analyze-lab/', views.analyze_lab, name='analyze_lab'),
    path('api/ask-grandma/', views.ask_grandma, name='ask_grandma'),

    # --- NEW PHYSICIAN HUB API ENDPOINTS ---
    path('api/generate-soap/', views.api_generate_soap, name='api_generate_soap'),
    path('api/referral/', views.api_specialist_referral, name='api_specialist_referral'),
    path('api/clinical-logic/', views.api_clinical_logic, name='api_clinical_logic'),
]