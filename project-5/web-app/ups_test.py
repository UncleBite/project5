from django.conf import settings
import django

from final_project.settings import DATABASES, INSTALLED_APPS
settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()

from UPS.models import *
print(Ups.objects.all()[0].any_fild)

test1 = Ups(account = 'ncnc12345', world_id = 1, package_id = 1, product_name = 'food', description = 'no description', count = 5, truckid = 1, location_x = 1, location_y = 1, status = 'open')
test1.save()


