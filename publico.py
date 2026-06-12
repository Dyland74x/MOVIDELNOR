from flask import Blueprint, render_template, jsonify
from models import Turno, Modulo

publico_bp = Blueprint('publico', __name__)

@publico_bp.route('/')
def pantalla_publica():
    return render_template('publico.html')

@publico_bp.route('/api/estado_por_modulo')
def api_estado_por_modulo():
    # Obtener todos los módulos activos
    modulos = Modulo.query.filter_by(activo=True).all()
    resultado = []
    for modulo in modulos:
        # Turno actual en atención (en_servicio o llamado, priorizamos en servicio)
        turno_actual = Turno.query.filter(
            Turno.id_modulo == modulo.id,
            Turno.estado.in_(['en_servicio', 'llamado'])
        ).order_by(Turno.estado.desc()).first()  # 'en_servicio' antes que 'llamado'
        # Turnos en espera
        turnos_espera = Turno.query.filter_by(
            id_modulo=modulo.id,
            estado='espera'
        ).order_by(Turno.creado_en).all()
        resultado.append({
            'modulo_id': modulo.id,
            'modulo_nombre': modulo.nombre,
            'modulo_codigo': modulo.codigo,
            'turno_actual': turno_actual.to_dict() if turno_actual else None,
            'turnos_espera': [t.to_dict() for t in turnos_espera]
        })
    return jsonify(resultado)