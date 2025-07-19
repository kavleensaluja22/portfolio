from django.urls import path, include
from . import views

app_name = 'portfolio'

urlpatterns = [
    # Main portfolio page (only needed route for SPA)
    path('', views.portfolio_home, name='home'),

    # Optional: class-based alternative for home view
    path('class-based/', views.PortfolioHomeView.as_view(), name='home_class'),

    # Utility views
    path('download-resume/', views.download_resume, name='download_resume'),
    path('contact-form/', views.ContactView.as_view(), name='contact_form'),

    # API endpoints
    path('api/send-message/', views.send_message, name='send_message'),
    path('api/projects/<int:project_id>/', views.project_detail, name='project_detail'),
]

# Admin-like custom management views (optional)
admin_urlpatterns = [
    path('manage/', include([
        path('', views.portfolio_home, name='manage_home'),
    ])),
]

# API structure for frontend fetching (optional if you're not using it)
api_urlpatterns = [
    path('api/v1/', include([
        path('profile/', views.about_section, name='api_profile'),
        path('projects/', views.projects_section, name='api_projects'),
        path('skills/', views.skills_section, name='api_skills'),
        path('contact/', views.send_message, name='api_contact'),
    ])),
]

# Combine all URL patterns
urlpatterns += admin_urlpatterns + api_urlpatterns
