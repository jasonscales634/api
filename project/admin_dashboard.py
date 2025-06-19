from django.contrib.admin import AdminSite

class CustomAdminSite(AdminSite):
    site_header = "ADCpa Custom Admin"
    site_title = "ADCpa Admin Portal"
    index_title = "Welcome to ADCpa Admin"
