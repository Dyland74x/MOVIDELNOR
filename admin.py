from flask import Blueprint, render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Turno, Modulo, Usuario, Rol
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO
import bcrypt

admin_bp = Blueprint('admin', __name__)

# ==================== DASHBOARD ====================
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.rol.nombre != 'Administrador':
        return "Acceso denegado", 403
    return render_template('admin_dashboard.html')

@admin_bp.route('/api/metricas')
@login_required
def metricas():
    filtro = request.args.get('filtro', 'dia')
    ahora = datetime.now()
    if filtro == 'dia':
        inicio = ahora.replace(hour=0, minute=0, second=0)
    elif filtro == 'semana':
        inicio = ahora - timedelta(days=7)
    else:
        inicio = ahora - timedelta(days=30)
    
    turnos_atendidos = Turno.query.filter(Turno.fin_atencion >= inicio).count()
    promedio = db.session.query(db.func.avg(db.func.timestampdiff(db.text('SECOND'), Turno.inicio_atencion, Turno.fin_atencion))).filter(Turno.fin_atencion >= inicio).scalar() or 0
    pendientes = Turno.query.filter_by(estado='espera').count()
    
    modulos = Modulo.query.all()
    data_modulos = []
    for m in modulos:
        count = Turno.query.filter_by(id_modulo=m.id, estado='finalizado').filter(Turno.fin_atencion >= inicio).count()
        data_modulos.append({'modulo': m.nombre, 'atendidos': count})
    
    return jsonify({
        'turnos_atendidos': turnos_atendidos,
        'promedio_segundos': round(promedio, 2),
        'pendientes': pendientes,
        'por_modulo': data_modulos
    })

# ==================== EXPORTAR REPORTES ====================
@admin_bp.route('/exportar/<formato>')
@login_required
def exportar(formato):
    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0)
    turnos = Turno.query.filter(Turno.creado_en >= inicio_mes).all()
    
    data = []
    for t in turnos:
        data.append({
            'Número': t.numero_turno,
            'Módulo': t.modulo.nombre if t.modulo else '',
            'Estado': t.estado,
            'Creado': t.creado_en.strftime('%Y-%m-%d %H:%M:%S') if t.creado_en else '',
            'Inicio atención': t.inicio_atencion.strftime('%Y-%m-%d %H:%M:%S') if t.inicio_atencion else '',
            'Fin atención': t.fin_atencion.strftime('%Y-%m-%d %H:%M:%S') if t.fin_atencion else '',
            'Funcionario': t.funcionario.nombre_completo if t.funcionario else ''
        })
    
    df = pd.DataFrame(data)
    
    if formato == 'excel':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Turnos')
            # Autoajustar ancho de columnas
            worksheet = writer.sheets['Turnos']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='reporte_turnos.xlsx'
        )
    
    elif formato == 'pdf':
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                                leftMargin=0.5*cm, rightMargin=0.5*cm,
                                topMargin=1*cm, bottomMargin=1*cm)
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        elements.append(Paragraph("Reporte de Turnos", styles['Title']))
        elements.append(Paragraph(" ", styles['Normal']))
        
        # Preparar tabla con wrap
        table_data = [['Número', 'Módulo', 'Estado', 'Creado', 'Inicio atención', 'Fin atención', 'Funcionario']]
        for row in data:
            modulo_para = Paragraph(row['Módulo'], styles['Normal'])
            funcionario_para = Paragraph(row['Funcionario'], styles['Normal'])
            table_data.append([
                row['Número'],
                modulo_para,
                row['Estado'],
                row['Creado'],
                row['Inicio atención'],
                row['Fin atención'],
                funcionario_para
            ])
        
        # Anchos de columna (puntos)
        col_widths = [80, 140, 70, 120, 120, 120, 120]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))
        elements.append(table)
        doc.build(elements)
        buffer.seek(0)
        return send_file(buffer,
                        mimetype='application/pdf',
                        as_attachment=True,
                        download_name='reporte_turnos.pdf')

# ==================== GESTIÓN DE USUARIOS ====================
@admin_bp.route('/usuarios')
@login_required
def usuarios():
    if current_user.rol.nombre != 'Administrador':
        return "Acceso denegado", 403
    usuarios = Usuario.query.all()
    modulos = Modulo.query.all()
    roles = Rol.query.all()
    return render_template('admin_usuarios.html', usuarios=usuarios, modulos=modulos, roles=roles)

@admin_bp.route('/usuarios/crear', methods=['POST'])
@login_required
def crear_usuario():
    data = request.form
    hashed = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    usuario = Usuario(
        username=data['username'],
        password_hash=hashed.decode('utf-8'),
        nombre_completo=data['nombre_completo'],
        id_rol=data['id_rol'],
        id_modulo=data.get('id_modulo') or None
    )
    db.session.add(usuario)
    db.session.commit()
    flash('Usuario creado correctamente')
    return redirect(url_for('admin.usuarios'))

@admin_bp.route('/usuarios/editar/<int:id>', methods=['POST'])
@login_required
def editar_usuario(id):
    usuario = Usuario.query.get(id)
    data = request.form
    usuario.username = data['username']
    usuario.nombre_completo = data['nombre_completo']
    usuario.id_rol = data['id_rol']
    usuario.id_modulo = data.get('id_modulo') or None
    if data.get('password'):
        usuario.password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db.session.commit()
    flash('Usuario actualizado')
    return redirect(url_for('admin.usuarios'))

@admin_bp.route('/usuarios/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_usuario(id):
    usuario = Usuario.query.get(id)
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado')
    return redirect(url_for('admin.usuarios'))

# ==================== GESTIÓN DE MÓDULOS ====================
@admin_bp.route('/modulos')
@login_required
def modulos():
    if current_user.rol.nombre != 'Administrador':
        return "Acceso denegado", 403
    modulos = Modulo.query.all()
    return render_template('admin_modulos.html', modulos=modulos)

@admin_bp.route('/modulos/crear', methods=['POST'])
@login_required
def crear_modulo():
    data = request.form
    modulo = Modulo(
        nombre=data['nombre'],
        codigo=data['codigo'],
        descripcion=data.get('descripcion'),
        activo=True
    )
    db.session.add(modulo)
    db.session.commit()
    flash('Módulo creado correctamente')
    return redirect(url_for('admin.modulos'))

@admin_bp.route('/modulos/editar/<int:id>', methods=['POST'])
@login_required
def editar_modulo(id):
    modulo = Modulo.query.get(id)
    data = request.form
    modulo.nombre = data['nombre']
    modulo.codigo = data['codigo']
    modulo.descripcion = data.get('descripcion')
    db.session.commit()
    flash('Módulo actualizado')
    return redirect(url_for('admin.modulos'))

@admin_bp.route('/modulos/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_modulo(id):
    modulo = Modulo.query.get(id)
    db.session.delete(modulo)
    db.session.commit()
    flash('Módulo eliminado')
    return redirect(url_for('admin.modulos'))