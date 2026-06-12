import bcrypt
import mysql.connector

# Conexión a MySQL (ajusta la contraseña si tu root tiene una)
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",        # Si tienes contraseña, escríbela aquí
    database="gestion_turnos"
)
cursor = conn.cursor()

# Obtener todos los módulos activos
cursor.execute("SELECT id, codigo, nombre FROM modulos WHERE activo = 1")
modulos = cursor.fetchall()

# Contraseña común para todos los funcionarios
password_default = "1234"
hashed = bcrypt.hashpw(password_default.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

for id_mod, codigo, nombre in modulos:
    # Verificar si ya existe un usuario con ese código
    cursor.execute("SELECT id FROM usuarios WHERE username = %s", (codigo,))
    if cursor.fetchone():
        print(f"⚠️ El usuario {codigo} ya existe. Se omite.")
        continue
    
    # Insertar funcionario
    cursor.execute("""
        INSERT INTO usuarios (username, password_hash, nombre_completo, id_rol, id_modulo, activo)
        VALUES (%s, %s, %s, 2, %s, 1)
    """, (codigo, hashed, f"Funcionario de {nombre}", id_mod))
    print(f"✅ Creado: {codigo} / {password_default} → {nombre}")

conn.commit()
cursor.close()
conn.close()
print("\n🎉 Todos los funcionarios han sido creados.")