import csv
import hmac
import io
import os
import secrets
from datetime import timedelta
from functools import wraps
from pathlib import Path

from flask import Flask, Response, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from backend.repository import Repository
from backend.service import Service, STATUSES, APPROVALS

ROOT = Path(__file__).resolve().parent.parent

def create_app(config=None):
    app = Flask(__name__, template_folder=str(ROOT / 'frontend' / 'templates'))
    data_dir = ROOT / 'instance'
    data_dir.mkdir(exist_ok=True)
    secret_path = data_dir / '.session-secret'
    if not secret_path.exists():
        secret_path.write_text(secrets.token_hex(32))
        secret_path.chmod(0o600)
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY') or secret_path.read_text().strip(),
        DATABASE=str(data_dir / 'techservice.sqlite3'),
        ADMIN_USER=os.environ.get('ADMIN_USER', 'admin'),
        ADMIN_PASSWORD_HASH=generate_password_hash(os.environ.get('ADMIN_PASSWORD', 'TechService123!')),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=4),
        MAX_CONTENT_LENGTH=64 * 1024,
    )
    if config:
        app.config.update(config)
    repo = Repository(app.config['DATABASE'])
    service = Service(repo)
    app.extensions['repository'] = repo
    app.extensions['service'] = service

    def csrf_token():
        if 'csrf' not in session:
            session['csrf'] = secrets.token_hex(32)
        return session['csrf']

    app.jinja_env.globals.update(csrf_token=csrf_token)
    app.jinja_env.filters['brl'] = lambda cents: ('R$ ' + f'{cents / 100:,.2f}').replace(',', '_').replace('.', ',').replace('_', '.')

    @app.before_request
    def protect_forms():
        if request.method == 'POST':
            actual = request.form.get('csrf', '')
            expected = session.get('csrf', '')
            if not expected or not hmac.compare_digest(actual, expected):
                abort(400, 'Formulário expirado. Atualize a página e tente novamente.')

    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'same-origin'
        response.headers['Cache-Control'] = 'no-store'
        return response

    def login_required(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if not session.get('authenticated'):
                return redirect(url_for('login'))
            return fn(*args, **kwargs)
        return wrapped

    def page(name, **kwargs):
        return render_template('app.html', page=name, statuses=STATUSES, approvals=APPROVALS, **kwargs)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            if hmac.compare_digest(request.form.get('username', ''), app.config['ADMIN_USER']) and check_password_hash(app.config['ADMIN_PASSWORD_HASH'], request.form.get('password', '')):
                session.clear()
                session['authenticated'] = True
                session.permanent = True
                return redirect(url_for('dashboard'))
            flash('Usuário ou senha incorretos.', 'error')
        return page('login')

    @app.post('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    @app.get('/')
    @login_required
    def dashboard():
        orders = repo.orders()
        counts = {status: sum(o['status'] == status for o in orders) for status in STATUSES}
        return page('dashboard', orders=orders[:8], counts=counts, total=len(orders), client_count=len(repo.clients()), equipment_count=len(repo.equipment()))

    @app.route('/clientes', methods=['GET', 'POST'])
    @login_required
    def clients():
        if request.method == 'POST':
            try:
                service.save_client(request.form)
                flash('Cliente salvo.', 'success')
                return redirect(url_for('clients'))
            except ValueError as error:
                flash(str(error), 'error')
        edit = None
        edit_id = request.args.get('edit', type=int)
        if edit_id:
            edit = repo.one('SELECT * FROM clients WHERE id=?', (edit_id,))
            if edit is None:
                abort(404)
        rows = repo.clients()
        q = request.args.get('q', '').strip()
        if q:
            rows = [r for r in rows if q.casefold() in (r['name'] + ' ' + r['phone'] + ' ' + r['email']).casefold()]
        return page('clients', clients=rows, edit=edit, q=q)

    @app.route('/equipamentos', methods=['GET', 'POST'])
    @login_required
    def equipment():
        if request.method == 'POST':
            try:
                service.create_equipment(request.form)
                flash('Equipamento cadastrado.', 'success')
                return redirect(url_for('equipment'))
            except ValueError as error:
                flash(str(error), 'error')
        return page('equipment', equipment=repo.equipment(), clients=repo.clients())

    @app.get('/ordens')
    @login_required
    def orders():
        q = request.args.get('q', '').strip().casefold()
        status = request.args.get('status', '')
        rows = repo.orders()
        rows = [o for o in rows if (not status or o['status'] == status) and (not q or q in (str(o['id']) + ' ' + o['client_name'] + ' ' + o['kind'] + ' ' + o['problem']).casefold())]
        return page('orders', orders=rows, q=request.args.get('q', ''), selected_status=status)

    @app.route('/ordens/nova', methods=['GET', 'POST'])
    @login_required
    def new_order():
        if request.method == 'POST':
            try:
                order_id = service.create_order(request.form)
                flash('Ordem de serviço aberta.', 'success')
                return redirect(url_for('order_detail', order_id=order_id))
            except ValueError as error:
                flash(str(error), 'error')
        return page('new_order', equipment=repo.equipment())

    @app.route('/ordens/<int:order_id>', methods=['GET', 'POST'])
    @login_required
    def order_detail(order_id):
        if repo.order(order_id) is None:
            abort(404)
        if request.method == 'POST':
            try:
                service.update_order(order_id, request.form)
                flash('Ordem atualizada. Alterações registradas no histórico.', 'success')
                return redirect(url_for('order_detail', order_id=order_id))
            except ValueError as error:
                flash(str(error), 'error')
        return page('detail', order=repo.order(order_id), history=repo.history(order_id))

    @app.get('/relatorio.csv')
    @login_required
    def report():
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter=';')
        writer.writerow(['OS', 'Cliente', 'Equipamento', 'Status', 'Aprovação', 'Orçamento R$', 'Técnico', 'Abertura UTC'])
        def safe(value):
            value = str(value)
            return "'" + value if value.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')) else value
        for order in repo.orders():
            writer.writerow([safe(v) for v in [order['id'], order['client_name'], order['kind'], order['status'], order['approval'], f"{order['budget_cents']/100:.2f}".replace('.', ','), order['technician'], order['created_at']]])
        return Response('\ufeff' + buffer.getvalue(), mimetype='text/csv; charset=utf-8', headers={'Content-Disposition': 'attachment; filename=techservice-ordens.csv'})

    @app.errorhandler(400)
    def bad_request(error):
        return page('error', message=error.description), 400

    @app.errorhandler(404)
    def not_found(error):
        return page('error', message='Registro ou página não encontrado.'), 404

    return app
