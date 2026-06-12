# audit.py
from flask import request
from models import db, Auditoria
import logging

logger = logging.getLogger(__name__)

class Auditoria:
    @staticmethod
    def registrar_accion(usuario_id, accion, modulo=None, turno_id=None, detalles=None):
        try:
            ip = request.remote_addr if request else None
            log = Auditoria(
                usuario_id=usuario_id,
                accion=accion,
                modulo=modulo,
                turno_id=turno_id,
                detalles=detalles,
                ip_address=ip
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            logger.error(f"Error al guardar auditoría: {e}")
            db.session.rollback()

    @staticmethod
    def registrar_error(error, usuario=None):
        ip = request.remote_addr if request else None
        logger.error(f"ERROR: usuario={usuario}, ip={ip}, error={error}")
