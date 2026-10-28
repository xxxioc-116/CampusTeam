from django.conf import settings
from django.db import models


class RecommendationProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recommendation_profile")
    abilities = models.JSONField(default=list)
    skills = models.JSONField(default=list)
    availability = models.JSONField(default=list)
    goal = models.CharField(max_length=100, blank=True)
    experience = models.CharField(max_length=500, blank=True)
    bio = models.TextField(blank=True)


class RecommendationRequirement(models.Model):
    team = models.OneToOneField("core.Team", on_delete=models.CASCADE, related_name="recommendation_requirement")
    abilities = models.JSONField(default=list)
    skills = models.JSONField(default=list)
    availability = models.JSONField(default=list)
    goal = models.CharField(max_length=100, blank=True)
    experience = models.CharField(max_length=500, blank=True)
    weights = models.JSONField(default=dict)
