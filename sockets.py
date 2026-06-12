from flask_socketio import emit, join_room

def init_socket_events(socketio):
    
    @socketio.on('join')
    def on_join(data):
        room = data.get('room')
        if room:
            join_room(room)
            print(f"📡 Dispositivo (Agente/Kiosco) unido a la sala: {room}")

    @socketio.on('imprimir_ticket')
    def handle_imprimir(data):
        print(f"📥 RECIBIDO DESDE WEB: {data}") # <-- ESTO ES CLAVE
    
        room = data.get('puesto_id') or data.get('room')
        contenido = data.get('contenido')
    
        print(f"📤 REENVIANDO A WINDOWS (SALA {room})...")
        emit('comando_imprimir', {'contenido': contenido}, room=room)