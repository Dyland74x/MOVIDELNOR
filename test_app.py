import unittest
import json
from app import app, db
from models import Usuario, Modulo, Turno

class TestSistemaTurnos(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            # Crear módulo de prueba
            modulo = Modulo(nombre='Test', codigo='TST', activo=True)
            db.session.add(modulo)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_generar_turno(self):
        # Simular login
        with self.app as client:
            # Crear usuario kiosco (mock)
            with app.app_context():
                usuario = Usuario(username='kiosco_test', password_hash='hash', id_rol=3)
                db.session.add(usuario)
                db.session.commit()
            # En una prueba real se usaría login, pero aquí se simplifica
            response = client.post('/kiosco/generar_turno',
                                   data=json.dumps({'modulo_id': 1}),
                                   content_type='application/json')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('turno', data)

    def test_obtener_turnos_espera(self):
        response = self.app.get('/funcionario/api/turnos_espera/1')
        # Sin autenticación debería dar 401
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()