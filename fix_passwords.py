import bcrypt
import mysql.connector

# Conexión a la base de datos (ajusta si tienes contraseña)
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="gestion_turnos"
)
cursor = conn.cursor()

# Generar hash para admin123
hash_admin = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
# Generar hash para kiosco
hash_kiosco = bcrypt.hashpw("kiosco".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Actualizar
cursor.execute("UPDATE usuarios SET password_hash = %s WHERE username = 'admin'", (hash_admin,))
cursor.execute("UPDATE usuarios SET password_hash = %s WHERE username = 'kiosco'", (hash_kiosco,))
conn.commit()

print("Contraseñas actualizadas correctamente")
cursor.close()
conn.close()