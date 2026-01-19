from django.forms.models import model_to_dict


def resolve_user_profile(user):
    profile_map = [
        ('member', 'member_profile'),
        ('investor', 'investor_profile'),
        ('startup', 'startup_profile'),
        ('cofounder', 'cofounder_profile'),
        ('incubator', 'incubator_profile'),
        ('revops', 'revops_profile'),
        ('cto', 'cto_profile'),
    ]

    for user_type, related_name in profile_map:
        if hasattr(user, related_name):
            profile = getattr(user, related_name)
            return user_type, profile

    return None, None






def serialize_profile(profile):
    return model_to_dict(profile, exclude=['id', 'user'])