from flask import Blueprint, jsonify
from models import Turno, Modulo
from flask_login import login_required

api_bp = Blueprint('api', __name__)

@api_bp.route('/turnos/estado/<modulo_id>')
@login_required
def turnos_estado(modulo_id):
    turnos = Turno.query.filter_by(id_modulo=modulo_id, estado='espera').all()
    return jsonify([t.to_dict() for t in turnos])

@api_bp.route('/modulos')
@login_required
def listar_modulos():
    modulos = Modulo.query.filter_by(activo=True).all()
    return jsonify([{'id': m.id, 'nombre': m.nombre, 'codigo': m.codigo} for m in modulos])