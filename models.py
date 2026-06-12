from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)

class Modulo(db.Model):
    __tablename__ = 'modulos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(10), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre_completo = db.Column(db.String(100))
    id_rol = db.Column(db.Integer, db.ForeignKey('roles.id'))
    id_modulo = db.Column(db.Integer, db.ForeignKey('modulos.id'))
    activo = db.Column(db.Boolean, default=True)

    rol = db.relationship('Rol')
    modulo = db.relationship('Modulo')

class Turno(db.Model):
    __tablename__ = 'turnos'
    id = db.Column(db.Integer, primary_key=True)
    numero_turno = db.Column(db.String(20), nullable=False)
    id_modulo = db.Column(db.Integer, db.ForeignKey('modulos.id'))
    estado = db.Column(db.Enum('espera', 'llamado', 'en_servicio', 'finalizado', 'transferido'), default='espera')
    creado_en = db.Column(db.DateTime, default=datetime.now)
    llamado_en = db.Column(db.DateTime, nullable=True)
    inicio_atencion = db.Column(db.DateTime, nullable=True)
    fin_atencion = db.Column(db.DateTime, nullable=True)
    id_funcionario_asignado = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    id_modulo_origen = db.Column(db.Integer, db.ForeignKey('modulos.id'))

    modulo = db.relationship('Modulo', foreign_keys=[id_modulo])
    funcionario = db.relationship('Usuario')

    def to_dict(self):
        return {
            'id': self.id,
            'numero_turno': self.numero_turno,
            'modulo': self.modulo.nombre if self.modulo else None,
            'modulo_id': self.id_modulo,
            'estado': self.estado,
            'creado_en': self.creado_en.strftime('%Y-%m-%d %H:%M:%S') if self.creado_en else None,
            'llamado_en': self.llamado_en.strftime('%Y-%m-%d %H:%M:%S') if self.llamado_en else None,
            'inicio_atencion': self.inicio_atencion.strftime('%Y-%m-%d %H:%M:%S') if self.inicio_atencion else None,
            'fin_atencion': self.fin_atencion.strftime('%Y-%m-%d %H:%M:%S') if self.fin_atencion else None,
            'funcionario': self.funcionario.nombre_completo if self.funcionario else None
        }

class DisponibilidadFuncionario(db.Model):
    __tablename__ = 'disponibilidad_funcionario'
    id = db.Column(db.Integer, primary_key=True)
    id_funcionario = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    id_modulo = db.Column(db.Integer, db.ForeignKey('modulos.id'))
    disponible = db.Column(db.Boolean, default=True)

# ==================== NUEVA TABLA DE AUDITORÍA ====================
class Auditoria(db.Model):
    __tablename__ = 'auditoria'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL'))
    accion = db.Column(db.String(100), nullable=False)
    modulo = db.Column(db.String(100))
    turno_id = db.Column(db.Integer, db.ForeignKey('turnos.id', ondelete='SET NULL'))
    detalles = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.now)

    usuario = db.relationship('Usuario', backref='auditoria_registros')
    turno = db.relationship('Turno', backref='auditoria_registros')