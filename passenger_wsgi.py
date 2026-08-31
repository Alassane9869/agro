import os
import sys

# Ajouter le chemin du projet au PYTHONPATH
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Définir le module de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrosedam.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
