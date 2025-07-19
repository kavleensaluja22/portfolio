from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
import json
import logging

from .models import Profile, Project, Skill, Education, Experience, ContactMessage
from .forms import ContactForm

logger = logging.getLogger(__name__)

class PortfolioHomeView(TemplateView):
    """
    Main portfolio view that displays all sections
    """
    template_name = 'portfolio/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            # Get or create profile (assuming single profile)
            profile, created = Profile.objects.get_or_create(
                id=1,
                defaults={
                    'name': 'Kavleen Kaur',
                    'title': 'Python Django Developer 🚀',
                    'hero_title': 'Python Django Developer',
                    'hero_description': 'Building magical web experiences with code! ✨🎭',
                    'about_description': 'Python Developer with 3+ years building modular, production-ready APIs, practicing strict TDD, and designing robust database schemas. Delivering clear developer docs and reliable CI/CD pipelines for scalable systems. I love turning complex problems into elegant solutions! ✨',
                    'email': 'work.kavleen@gmail.com',
                    'phone': '+91 8569893923',
                }
            )

            context.update({
                'profile': profile,
                'projects': profile.projects.filter(is_featured=True)[:6],
                'skills': profile.skills.all(),
                'education': profile.education.all(),
                'experiences': profile.experiences.all(),
                'contact_form': ContactForm(),
            })

        except Exception as e:
            logger.error(f"Error loading portfolio data: {e}")
            context['error'] = "Unable to load portfolio data"

        return context

def portfolio_home(request):
    """
    Function-based view for portfolio home page
    """
    try:
        # Get or create profile
        profile, created = Profile.objects.get_or_create(
            id=1,
            defaults={
                'name': 'Kavleen Kaur',
                'title': 'Python Django Developer 🚀',
                'hero_title': 'Python Django Developer',
                'hero_description': 'Building magical web experiences with code! ✨🎭',
                'about_description': 'Python Developer with 3+ years building modular, production-ready APIs, practicing strict TDD, and designing robust database schemas. Delivering clear developer docs and reliable CI/CD pipelines for scalable systems. I love turning complex problems into elegant solutions! ✨',
                'email': 'work.kavleen@gmail.com',
                'phone': '+91 8569893923',
            }
        )

        # Get related data
        projects = profile.projects.filter(is_featured=True).order_by('order')[:6]
        skills = profile.skills.all()
        education = profile.education.all()
        experiences = profile.experiences.all()

        context = {
            'profile': profile,
            'projects': projects,
            'skills': skills,
            'education': education,
            'experiences': experiences,
            'contact_form': ContactForm(),
        }

        return render(request, 'portfolio/index.html', context)

    except Exception as e:
        logger.error(f"Error in portfolio_home view: {e}")
        return render(request, 'portfolio/error.html', {'error': str(e)})

def about_section(request):
    """
    View for about section data (AJAX endpoint)
    """
    try:
        profile = get_object_or_404(Profile, id=1)
        education = profile.education.all()
        experiences = profile.experiences.all()

        data = {
            'about_description': profile.about_description,
            'education': [
                {
                    'degree': edu.degree,
                    'description': edu.description,
                    'icon': edu.icon
                } for edu in education
            ],
            'experiences': [
                {
                    'title': exp.title,
                    'description': exp.description,
                    'icon': exp.icon
                } for exp in experiences
            ]
        }

        return JsonResponse(data)

    except Exception as e:
        logger.error(f"Error in about_section view: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def projects_section(request):
    """
    View for projects section (can be used for AJAX or full page)
    """
    try:
        profile = get_object_or_404(Profile, id=1)
        projects = profile.projects.all()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX request - return JSON
            data = {
                'projects': [
                    {
                        'title': project.title,
                        'description': project.description,
                        'technologies': project.get_technologies_list(),
                        'icon': project.icon,
                        'project_url': project.project_url,
                        'github_url': project.github_url,
                    } for project in projects
                ]
            }
            return JsonResponse(data)
        else:
            # Regular request - return template
            context = {
                'profile': profile,
                'projects': projects,
            }
            return render(request, 'portfolio/projects.html', context)

    except Exception as e:
        logger.error(f"Error in projects_section view: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        return render(request, 'portfolio/error.html', {'error': str(e)})

def skills_section(request):
    """
    View for skills section data
    """
    try:
        profile = get_object_or_404(Profile, id=1)
        skills = profile.skills.all()

        # Group skills by category
        skills_by_category = {}
        for skill in skills:
            category = skill.get_category_display()
            if category not in skills_by_category:
                skills_by_category[category] = []
            skills_by_category[category].append({
                'name': skill.name,
                'proficiency_level': skill.proficiency_level,
            })

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'skills_by_category': skills_by_category})
        else:
            context = {
                'profile': profile,
                'skills': skills,
                'skills_by_category': skills_by_category,
            }
            return render(request, 'portfolio/skills.html', context)

    except Exception as e:
        logger.error(f"Error in skills_section view: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        return render(request, 'portfolio/error.html', {'error': str(e)})

@require_http_methods(["GET", "POST"])
def contact_section(request):
    """
    View for contact section - handles both display and form submission
    """
    try:
        profile = get_object_or_404(Profile, id=1)

        if request.method == 'POST':
            form = ContactForm(request.POST)

            if form.is_valid():
                # Save contact message
                contact_message = ContactMessage.objects.create(
                    name=form.cleaned_data['name'],
                    email=form.cleaned_data['email'],
                    subject=form.cleaned_data.get('subject', ''),
                    message=form.cleaned_data['message']
                )

                # Send email notification (optional)
                try:
                    send_mail(
                        subject=f"Portfolio Contact: {contact_message.subject or 'New Message'}",
                        message=f"""
                        New contact message from portfolio:

                        Name: {contact_message.name}
                        Email: {contact_message.email}
                        Subject: {contact_message.subject}

                        Message:
                        {contact_message.message}
                        """,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[profile.email],
                        fail_silently=True,
                    )
                except Exception as email_error:
                    logger.warning(f"Failed to send email notification: {email_error}")

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Thank you for your message! I\'ll get back to you soon.'
                    })
                else:
                    messages.success(request, 'Thank you for your message! I\'ll get back to you soon.')
                    return redirect('portfolio:home')

            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'errors': form.errors
                    })
                else:
                    messages.error(request, 'Please correct the errors below.')

        else:
            form = ContactForm()

        context = {
            'profile': profile,
            'contact_form': form,
        }

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return contact info as JSON for AJAX requests
            return JsonResponse({
                'email': profile.email,
                'phone': profile.phone,
                'github_url': profile.github_url,
                'linkedin_url': profile.linkedin_url,
            })

        return render(request, 'portfolio/contact.html', context)

    except Exception as e:
        logger.error(f"Error in contact_section view: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        return render(request, 'portfolio/error.html', {'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """
    API endpoint for sending contact messages
    """
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        form = ContactForm(data)

        if form.is_valid():
            contact_message = ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                subject=form.cleaned_data.get('subject', ''),
                message=form.cleaned_data['message']
            )

            return JsonResponse({
                'success': True,
                'message': 'Message sent successfully!',
                'message_id': contact_message.id
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in send_message view: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

def project_detail(request, project_id):
    """
    View for individual project details
    """
    try:
        project = get_object_or_404(Project, id=project_id)

        context = {
            'project': project,
            'technologies': project.get_technologies_list(),
        }

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = {
                'title': project.title,
                'description': project.description,
                'technologies': project.get_technologies_list(),
                'icon': project.icon,
                'project_url': project.project_url,
                'github_url': project.github_url,
                'created_at': project.created_at.isoformat(),
            }
            return JsonResponse(data)

        return render(request, 'portfolio/project_detail.html', context)

    except Exception as e:
        logger.error(f"Error in project_detail view: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        return render(request, 'portfolio/error.html', {'error': str(e)})

def download_resume(request):
    """
    View for downloading resume/CV
    """
    try:
        # This would typically serve a PDF file
        # For now, return a simple response
        response = HttpResponse(
            "Resume download functionality would be implemented here.",
            content_type='text/plain'
        )
        response['Content-Disposition'] = 'attachment; filename="Kavleen_Kaur_Resume.txt"'
        return response

    except Exception as e:
        logger.error(f"Error in download_resume view: {e}")
        return HttpResponse("Error downloading resume", status=500)

# Class-based view alternative for contact
class ContactView(CreateView):
    model = ContactMessage
    form_class = ContactForm
    template_name = 'portfolio/contact.html'
    success_url = reverse_lazy('portfolio:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(Profile, id=1)
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Thank you for your message! I\'ll get back to you soon.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
