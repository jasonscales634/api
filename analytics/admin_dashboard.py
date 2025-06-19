from django.contrib.admin import AdminSite

class CustomAdminSite(AdminSite):
    site_header = "Custom Admin"
    site_title = "Admin Panel"
    index_title = "Welcome to the Admin Dashboard"

# ✅ Add this line:
custom_admin_site = CustomAdminSite(name='custom_admin')
