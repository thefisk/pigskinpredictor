from rest_framework import permissions

class IsSuperUser(permissions.BasePermission): 
    def has_permission(self, request, view):
        return request.user.groups.filter(name='SuperUser').exists()