from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import User


class IsAdminRole(BasePermission):
    message = "仅管理员可执行此操作"

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == User.Role.ADMIN)


class IsProjectOwnerOrReadOnly(BasePermission):
    message = "仅项目负责人可以修改项目"

    def has_object_permission(self, request, view, obj):
        if getattr(view, "action", None) == "applications" and request.method == "POST":
            return True
        return request.method in SAFE_METHODS or obj.owner_id == request.user.id or request.user.role == User.Role.ADMIN


class IsTeamLeader(BasePermission):
    message = "仅队长可以邀请成员"

    def has_object_permission(self, request, view, obj):
        return obj.leader_id == request.user.id or request.user.role == User.Role.ADMIN

