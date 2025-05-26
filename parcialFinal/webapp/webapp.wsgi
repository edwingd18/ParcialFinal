import sys
import os

# 1) Añade tu proyecto al path de Python
project_path = '/home/vagrant/webapp'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# 2) (Opcional) Si usas un virtualenv, activa su intérprete:
# activate_this = '/home/vagrant/webapp/venv/bin/activate_this.py'
# with open(activate_this) as f:
#     exec(f.read(), dict(__file__=activate_this))

# 3) Exporta la variable FLASK_APP para que mod_wsgi la reconozca
os.environ.setdefault('FLASK_APP', 'run.py')

# 4) Importa tu app como WSGI application
from web.views import app as application

