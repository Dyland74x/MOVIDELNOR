import sys
import os

# 1. Definir la ruta base del proyecto
BASE_DIR = '/var/www/FLASK'

# 2. Definir la ruta del entorno virtual (activación manual)
venv_bin = os.path.join(BASE_DIR, 'venv/bin/activate_this.py')

# 3. Intentar activar el venv usando el script de activación
if os.path.exists(venv_bin):
    with open(venv_bin) as f:
        code = compile(f.read(), venv_bin, 'exec')
        exec(code, dict(__file__=venv_bin))
else:
    # Si no existe activate_this.py (común en Python 3), añadimos los site-packages a mano
    # AJUSTA LA VERSIÓN DE PYTHON (3.9) SI ES NECESARIO
    site_packages = os.path.join(BASE_DIR, 'venv/lib/python3.9/site-packages')
    sys.path.insert(0, site_packages)

# 4. Añadir la carpeta del proyecto al path
sys.path.insert(0, BASE_DIR)

# 5. Importar la aplicación
from app import app as application