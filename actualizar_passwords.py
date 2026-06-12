import bcrypt
import mysql.connector

# Conecta a MySQL (ajusta la contraseña si tienes)
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",      # Si tu root tiene contraseña, escríbela aquí
    database="gestion_turnos"
)
cursor = conn.cursor()

# Hashes correctos con bcrypt
hash_admin = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
hash_kiosco = bcrypt.hashpw("kiosco".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Actualizar
cursor.execute("UPDATE usuarios SET password_hash = %s WHERE username = 'admin'", (hash_admin,))
cursor.execute("UPDATE usuarios SET password_hash = %s WHERE username = 'kiosco'", (hash_kiosco,))

# Si quieres crear un funcionario de ejemplo (opcional)
# cursor.execute("INSERT INTO usuarios (username, password_hash, nombre_completo, id_rol, id_modulo) VALUES ('funcionario1', %s, 'Funcionario 1', 2, 1)", (bcrypt.hashpw("1234".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),))

conn.commit()
print("✅ Contraseñas actualizadas correctamente")
cursor.close()
conn.close()