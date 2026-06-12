from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models import db, Usuario
import bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            login_user(user)
            if user.rol.nombre == 'Administrador':
                return redirect(url_for('admin.dashboard'))
            elif user.rol.nombre == 'Funcionario':
                return redirect(url_for('funcionario.panel'))
            elif user.rol.nombre == 'Kiosco':
                return redirect(url_for('kiosco.index'))
        flash('Credenciales inválidas')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))