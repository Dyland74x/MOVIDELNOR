from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, Turno, Modulo, DisponibilidadFuncionario
from datetime import datetime
import re
import logging
from audit import Auditoria
from utils import retry_on_failure

logger = logging.getLogger(__name__)
funcionario_bp = Blueprint('funcionario', __name__)

def requiere_funcionario(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.rol.nombre != 'Funcionario':
            return jsonify({'error': 'Acceso denegado, solo funcionarios'}), 403
        return f(*args, **kwargs)
    return decorated

@funcionario_bp.route('/panel')
@login_required
@requiere_funcionario
def panel():
    # Módulos que puede atender (barra lateral)
    if current_user.modulo and current_user.modulo.codigo == 'JEFE':
        modulos_atencion = Modulo.query.filter_by(activo=True).all()
    else:
        modulos_atencion = [current_user.modulo] if current_user.modulo else []
    
    # Módulos a los que puede transferir (todos los activos)
    modulos_transferencia = Modulo.query.filter_by(activo=True).all()
    
    return render_template('funcionario.html', 
                           modulos_atencion=modulos_atencion,
                           modulos_transferencia=modulos_transferencia,
                           usuario=current_user)

@funcionario_bp.route('/api/turnos_espera/<int:modulo_id>')
@login_required
@requiere_funcionario
def api_turnos_espera(modulo_id):
    if current_user.modulo and current_user.modulo.codigo != 'JEFE' and current_user.id_modulo != modulo_id:
        return jsonify({'error': 'No autorizado'}), 403
    turnos = Turno.query.filter_by(id_modulo=modulo_id, estado='espera').order_by(Turno.creado_en).all()
    return jsonify([t.to_dict() for t in turnos])

@funcionario_bp.route('/api/turno_actual')
@login_required
@requiere_funcionario
def api_turno_actual():
    turno = Turno.query.filter(
        Turno.id_funcionario_asignado == current_user.id,
        Turno.estado == 'en_servicio'
    ).first()
    return jsonify(turno.to_dict() if turno else None)

@retry_on_failure(max_retries=2, delay=1)
@funcionario_bp.route('/siguiente', methods=['POST'])
@login_required
@requiere_funcionario
def siguiente_turno():
    data = request.get_json()
    modulo_id = data.get('modulo_id')
    if current_user.modulo and current_user.modulo.codigo != 'JEFE' and current_user.id_modulo != modulo_id:
        return jsonify({'error': 'No autorizado'}), 403

    turno = Turno.query.filter_by(id_modulo=modulo_id, estado='espera').order_by(Turno.creado_en).first()
    if not turno:
        return jsonify({'error': 'No hay turnos en espera'}), 404

    turno.estado = 'en_servicio'
    turno.llamado_en = datetime.now()
    turno.inicio_atencion = datetime.now()
    turno.id_funcionario_asignado = current_user.id
    db.session.commit()
    Auditoria.registrar_accion(current_user.id, 'llamar_turno', turno.modulo.nombre, turno.id)
    return jsonify(turno.to_dict())

@funcionario_bp.route('/finalizar', methods=['POST'])
@login_required
@requiere_funcionario
def finalizar_turno():
    data = request.get_json()
    turno_id = data.get('turno_id')
    turno = Turno.query.get(turno_id)
    if not turno or turno.id_funcionario_asignado != current_user.id:
        return jsonify({'error': 'Turno no válido'}), 400
    if turno.estado == 'en_servicio':
        turno.estado = 'finalizado'
        turno.fin_atencion = datetime.now()
        db.session.commit()
        Auditoria.registrar_accion(current_user.id, 'finalizar_turno', turno.modulo.nombre, turno.id)
        return jsonify({'ok': True})
    return jsonify({'error': 'Estado inválido'}), 400

@funcionario_bp.route('/transferir', methods=['POST'])
@login_required
@requiere_funcionario
def transferir_turno():
    data = request.get_json()
    turno_id = data.get('turno_id')
    nuevo_modulo_id = data.get('nuevo_modulo_id')
    turno = Turno.query.get(turno_id)
    if not turno or turno.id_funcionario_asignado != current_user.id:
        return jsonify({'error': 'Turno no válido'}), 400
    
    # Conserva el mismo número, solo cambia de módulo
    turno.id_modulo_origen = turno.id_modulo
    turno.id_modulo = nuevo_modulo_id
    turno.estado = 'espera'
    turno.id_funcionario_asignado = None
    turno.llamado_en = None
    turno.inicio_atencion = None
    turno.fin_atencion = None
    db.session.commit()
    Auditoria.registrar_accion(current_user.id, 'transferir_turno', None, turno.id, {'nuevo_modulo': nuevo_modulo_id})
    return jsonify({'ok': True})

@funcionario_bp.route('/disponibilidad', methods=['POST'])
@login_required
@requiere_funcionario
def toggle_disponibilidad():
    data = request.get_json()
    modulo_id = data.get('modulo_id')
    disponible = data.get('disponible')
    disp = DisponibilidadFuncionario.query.filter_by(id_funcionario=current_user.id, id_modulo=modulo_id).first()
    if not disp:
        disp = DisponibilidadFuncionario(id_funcionario=current_user.id, id_modulo=modulo_id)
        db.session.add(disp)
    disp.disponible = disponible
    db.session.commit()
    return jsonify({'disponible': disp.disponible})

@funcionario_bp.route('/disponibilidad_status')
@login_required
@requiere_funcionario
def disponibilidad_status():
    modulo_id = request.args.get('modulo', type=int)
    if not modulo_id:
        return jsonify({'error': 'Falta parámetro modulo'}), 400
    disp = DisponibilidadFuncionario.query.filter_by(id_funcionario=current_user.id, id_modulo=modulo_id).first()
    disponible = disp.disponible if disp else True
    return jsonify({'disponible': disponible})