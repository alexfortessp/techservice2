import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA = '''
CREATE TABLE IF NOT EXISTS clients (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL, phone TEXT NOT NULL DEFAULT '', email TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS equipment (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 client_id INTEGER NOT NULL REFERENCES clients(id),
 kind TEXT NOT NULL, brand TEXT NOT NULL DEFAULT '', serial TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS orders (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 equipment_id INTEGER NOT NULL REFERENCES equipment(id),
 problem TEXT NOT NULL, technician TEXT NOT NULL DEFAULT '',
 diagnosis TEXT NOT NULL DEFAULT '', budget_cents INTEGER NOT NULL DEFAULT 0 CHECK(budget_cents >= 0),
 approval TEXT NOT NULL DEFAULT 'Pendente' CHECK(approval IN ('Pendente','Aprovado','Recusado')),
 status TEXT NOT NULL DEFAULT 'Aberta', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS history (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 order_id INTEGER NOT NULL REFERENCES orders(id),
 event TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
'''

class Repository:
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db:
            db.executescript(SCHEMA)

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys = ON')
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def all(self, query, params=()):
        with self.connection() as db:
            return [dict(row) for row in db.execute(query, params).fetchall()]

    def one(self, query, params=()):
        rows = self.all(query, params)
        return rows[0] if rows else None

    def execute(self, query, params=()):
        with self.connection() as db:
            return db.execute(query, params).lastrowid

    def clients(self):
        return self.all('SELECT * FROM clients ORDER BY name')

    def equipment(self):
        return self.all('SELECT e.*, c.name AS client_name FROM equipment e JOIN clients c ON c.id=e.client_id ORDER BY e.id DESC')

    def orders(self):
        return self.all('''SELECT o.*, e.kind, e.brand, c.name AS client_name
          FROM orders o JOIN equipment e ON e.id=o.equipment_id
          JOIN clients c ON c.id=e.client_id ORDER BY o.id DESC''')

    def order(self, order_id):
        return self.one('''SELECT o.*, e.kind, e.brand, e.serial, c.name AS client_name,
          c.phone AS client_phone FROM orders o JOIN equipment e ON e.id=o.equipment_id
          JOIN clients c ON c.id=e.client_id WHERE o.id=?''', (order_id,))

    def create_order(self, equipment_id, problem, technician):
        with self.connection() as db:
            order_id = db.execute('INSERT INTO orders(equipment_id,problem,technician) VALUES(?,?,?)',
                                  (equipment_id, problem, technician)).lastrowid
            db.execute('INSERT INTO history(order_id,event) VALUES(?,?)', (order_id, 'Ordem de serviço aberta.'))
            return order_id

    def update_order(self, order_id, technician, diagnosis, cents, approval, status):
        with self.connection() as db:
            old = db.execute('SELECT * FROM orders WHERE id=?', (order_id,)).fetchone()
            if old is None:
                raise ValueError('Ordem de serviço não encontrada.')
            db.execute('''UPDATE orders SET technician=?, diagnosis=?, budget_cents=?, approval=?, status=? WHERE id=?''',
                       (technician, diagnosis, cents, approval, status, order_id))
            changes = []
            for label, key, value in [('Técnico','technician',technician),('Diagnóstico','diagnosis',diagnosis),
                                      ('Orçamento (centavos)','budget_cents',cents),('Aprovação','approval',approval),('Status','status',status)]:
                if old[key] != value:
                    changes.append(f'{label}: {old[key]} → {value}')
            if changes:
                db.execute('INSERT INTO history(order_id,event) VALUES(?,?)', (order_id, '; '.join(changes)))

    def history(self, order_id):
        return self.all('SELECT * FROM history WHERE order_id=? ORDER BY id DESC', (order_id,))
