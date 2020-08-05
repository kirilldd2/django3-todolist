from .models import GroupUser


def invites_processor(request):
    try:
        invites = GroupUser.objects.filter(user=request.user, status='I')
        return {'invites': invites}
    except TypeError:
        return {}