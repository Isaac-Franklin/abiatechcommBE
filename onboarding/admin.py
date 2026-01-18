from django.contrib import admin
from onboarding.models import *

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(MemberProfile)
admin.site.register(InvestorProfile)
admin.site.register(StartupProfile)
admin.site.register(CofounderProfile)
admin.site.register(IncubatorProfile)
admin.site.register(RevOpsProfile)
admin.site.register(CTOProfile)