from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Profile, Project, Skill, Education, Experience, ContactMessage

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'email', 'updated_at']
    fields = [
        'name', 'title', 'hero_title', 'hero_description',
        'about_description', 'email', 'phone',
        'github_url', 'linkedin_url'
    ]
    readonly_fields = ['created_at', 'updated_at']

    def has_add_permission(self, request):
        # Only allow one profile instance
        return not Profile.objects.exists()

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_featured', 'order', 'created_at', 'view_links']
    list_filter = ['is_featured', 'created_at']
    search_fields = ['title', 'description', 'technologies']
    list_editable = ['is_featured', 'order']
    ordering = ['order', '-created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'icon')
        }),
        ('Technical Details', {
            'fields': ('technologies',)
        }),
        ('Links', {
            'fields': ('project_url', 'github_url')
        }),
        ('Display Options', {
            'fields': ('is_featured', 'order')
        }),
    )

    def view_links(self, obj):
        links = []
        if obj.project_url:
            links.append(f'<a href="{obj.project_url}" target="_blank">🔗 Live</a>')
        if obj.github_url:
            links.append(f'<a href="{obj.github_url}" target="_blank">🐙 GitHub</a>')
        return mark_safe(' | '.join(links)) if links else '-'
    view_links.short_description = 'Links'

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'proficiency_level', 'order']
    list_filter = ['category']
    search_fields = ['name']
    list_editable = ['category', 'proficiency_level', 'order']
    ordering = ['category', 'order']

    fieldsets = (
        ('Skill Information', {
            'fields': ('name', 'category', 'proficiency_level')
        }),
        ('Display Options', {
            'fields': ('order',)
        }),
    )

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['degree', 'icon', 'order']
    list_editable = ['order']
    ordering = ['order']

    fields = ['degree', 'description', 'icon', 'order']

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'icon', 'order']
    list_editable = ['order']
    ordering = ['order']

    fields = ['title', 'description', 'icon', 'order']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at', 'message_preview']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at']
    list_editable = ['is_read']
    ordering = ['-created_at']

    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'subject')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Status', {
            'fields': ('is_read', 'created_at')
        }),
    )

    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message Preview'

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} messages marked as read.')
    mark_as_read.short_description = 'Mark selected messages as read'

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} messages marked as unread.')
    mark_as_unread.short_description = 'Mark selected messages as unread'

# Customize admin site headers
admin.site.site_header = "Kavleen's Portfolio Admin"
admin.site.site_title = "Portfolio Admin"
admin.site.index_title = "Welcome to Portfolio Administration"
