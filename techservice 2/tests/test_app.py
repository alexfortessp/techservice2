import re
import tempfile
import unittest
from pathlib import Path
from backend.controller import create_app
from backend.repository import Repository
from backend.service import Service

class BusinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'db.sqlite3'
        self.repo = Repository(self.path)
        self.service = Service(self.repo)
        self.client_id = self.service.save_client({'name': 'Cliente Teste'})
        self.equipment_id = self.service.create_equipment({'client_id': self.client_id, 'kind': 'Notebook'})

    def tearDown(self):
        self.temp.cleanup()

    def order(self):
        return self.service.create_order({'equipment_id': self.equipment_id, 'problem': 'Não liga', 'technician': 'Técnico Teste'})

    def test_client_required(self):
        with self.assertRaises(ValueError):
            self.service.save_client({'name': '   '})

    def test_client_update(self):
        self.service.save_client({'id': self.client_id, 'name': 'Nome alterado'})
        self.assertEqual(self.repo.clients()[0]['name'], 'Nome alterado')

    def test_equipment_owner_validation(self):
        with self.assertRaises(ValueError):
            self.service.create_equipment({'client_id': 999999, 'kind': 'Notebook'})

    def test_order_problem_required(self):
        with self.assertRaises(ValueError):
            self.service.create_order({'equipment_id': self.equipment_id, 'problem': ''})

    def test_persistence(self):
        oid = self.order()
        other = Repository(self.path)
        self.assertEqual(other.order(oid)['problem'], 'Não liga')

    def test_money(self):
        self.assertEqual(self.service.money('150,50'), 15050)
        for bad in ('-1', 'NaN', 'Infinity', '1.234', 'abc'):
            with self.assertRaises(ValueError):
                self.service.money(bad)

    def test_approval_required(self):
        oid = self.order()
        with self.assertRaises(ValueError):
            self.service.update_order(oid, {'technician': 'Técnico', 'diagnosis': 'Fonte danificada', 'budget': '150', 'approval': 'Pendente', 'status': 'Em reparo'})
        self.assertEqual(self.repo.order(oid)['status'], 'Aberta')

    def test_complete_delivery_and_history(self):
        oid = self.order()
        data = {'technician': 'Técnico', 'diagnosis': 'Fonte danificada', 'budget': '150', 'approval': 'Aprovado', 'status': 'Concluída'}
        self.service.update_order(oid, data)
        data['status'] = 'Entregue'
        self.service.update_order(oid, data)
        self.assertEqual(self.repo.order(oid)['status'], 'Entregue')
        self.assertEqual(len(self.repo.history(oid)), 3)
        with self.assertRaises(ValueError):
            self.service.update_order(oid, data)

    def test_delivery_requires_conclusion(self):
        oid = self.order()
        with self.assertRaises(ValueError):
            self.service.update_order(oid, {'technician': 'Técnico', 'diagnosis': 'Defeito', 'budget': '1', 'approval': 'Aprovado', 'status': 'Entregue'})

    def test_approved_budget_changes_require_new_approval(self):
        oid = self.order()
        data = {'technician': 'Técnico', 'diagnosis': 'Defeito', 'budget': '100', 'approval': 'Aprovado', 'status': 'Aguardando aprovação'}
        self.service.update_order(oid, data)
        data['budget'] = '200'
        with self.assertRaises(ValueError):
            self.service.update_order(oid, data)

class HttpTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app({'TESTING': True, 'SECRET_KEY': 'test-only', 'DATABASE': str(Path(self.temp.name) / 'db.sqlite3')})
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp.cleanup()

    def csrf(self, path='/login'):
        body = self.client.get(path).get_data(as_text=True)
        return re.search(r'name="csrf" value="([^"]+)"', body).group(1)

    def login(self):
        return self.client.post('/login', data={'csrf': self.csrf(), 'username': 'admin', 'password': 'TechService123!'})

    def test_private_routes(self):
        self.assertEqual(self.client.get('/clientes').status_code, 302)
        self.assertEqual(self.client.get('/relatorio.csv').status_code, 302)

    def test_bad_login(self):
        r = self.client.post('/login', data={'csrf': self.csrf(), 'username': 'admin', 'password': 'wrong'})
        self.assertIn('incorretos', r.get_data(as_text=True))
        self.assertEqual(self.client.get('/').status_code, 302)

    def test_csrf(self):
        self.assertEqual(self.client.post('/login', data={'username': 'admin'}).status_code, 400)

    def test_login_create_and_report(self):
        self.assertEqual(self.login().status_code, 302)
        token = self.csrf('/clientes')
        self.assertEqual(self.client.post('/clientes', data={'csrf': token, 'name': 'Teste'}).status_code, 302)
        self.assertIn('Teste', self.client.get('/clientes').get_data(as_text=True))
        self.assertEqual(self.client.get('/relatorio.csv').status_code, 200)

    def test_html_escape(self):
        self.login()
        self.client.post('/clientes', data={'csrf': self.csrf('/clientes'), 'name': '<script>alert(1)</script>'})
        body = self.client.get('/clientes').get_data(as_text=True)
        self.assertNotIn('<script>alert(1)</script>', body)
        self.assertIn('&lt;script&gt;', body)

if __name__ == '__main__':
    unittest.main()
