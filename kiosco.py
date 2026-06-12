import re
import logging
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, Turno, Modulo
from datetime import datetime
from utils import imprimir_ticket
from audit import Auditoria

logger = logging.getLogger(__name__)
kiosco_bp = Blueprint('kiosco', __name__)

@kiosco_bp.route('/')
@login_required
def index():
    if current_user.rol.nombre != 'Kiosco':
        return "Acceso denegado", 403
    modulos = Modulo.query.filter_by(activo=True).all()
    return render_template('kiosco.html', modulos=modulos)

from datetime import datetime, date

from datetime import date # Importamos date para obtener la fecha de hoy sin hora

from datetime import datetime, time

def obtener_siguiente_numero(modulo_id, codigo_modulo):
    ahora = datetime.now()
    inicio_dia = datetime.combine(ahora.date(), time.min)
    fin_dia = datetime.combine(ahora.date(), time.max)

    ultimo_turno = Turno.query.filter(
        Turno.id_modulo == modulo_id,
        Turno.creado_en >= inicio_dia,
        Turno.creado_en <= fin_dia
    ).order_by(Turno.id.desc()).first()

    if ultimo_turno:
        try:
            # Extraemos el número final (ej: de "A-001" toma "001")
            ultimo_num_str = ultimo_turno.numero_turno.split('-')[-1]
            siguiente_num = int(ultimo_num_str) + 1
        except (ValueError, IndexError):
            siguiente_num = 1
    else:
        siguiente_num = 1

    # Formateamos el número para que tenga 3 dígitos con ceros a la izquierda
    # f"{siguiente_num:03}" convierte 1 en "001", 15 en "015", etc.
    nuevo_num_formateado = f"{siguiente_num:03}"

    return f"{codigo_modulo}-{nuevo_num_formateado}"

@kiosco_bp.route('/generar_turno', methods=['POST'])
@login_required

def generar_turno(): 
    data = request.get_json()
    modulo_id = data.get('modulo_id')
    modulo = Modulo.query.get(modulo_id)
    
    if not modulo:
        return jsonify({'error': 'Módulo inválido'}), 400

    try:
        # La lógica de reinicio ahora ocurre aquí dentro
        nuevo_num = obtener_siguiente_numero(modulo_id, modulo.codigo)
        
        turno = Turno(
            numero_turno=nuevo_num,
            id_modulo=modulo_id,
            estado='espera',
            creado_en=datetime.now() # Importante para que el filtro de fecha funcione
        )
        
        db.session.add(turno)
        db.session.commit()
        
        # ... resto de tu código (Auditoria e Impresión) ...
        
    except Exception as e:
        db.session.rollback() # Siempre hacer rollback en caso de error
        logger.error(f"Error generando turno: {e}")
        return jsonify({'error': str(e)}), 500

    return jsonify({'turno': nuevo_num, 'modulo': modulo.nombre}) 
