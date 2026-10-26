from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Application, AuditLog, Invitation, Project, ProjectSkillRequirement, Skill, Team, TeamMember, User, UserSkill

admin.site.register(User, UserAdmin)
for model in [Skill, UserSkill, Project, ProjectSkillRequirement, Team, TeamMember, Application, Invitation, AuditLog]:
    admin.site.register(model)

