from decimal import Decimal, InvalidOperation

STATUSES = ('Aberta', 'Em diagnóstico', 'Aguardando aprovação', 'Em reparo', 'Concluída', 'Entregue', 'Cancelada')
APPROVALS = ('Pendente', 'Aprovado', 'Recusado')

class Service:
    def __init__(self, repo):
        self.repo = repo

    @staticmethod
    def text(value, label, limit=200, required=False):
        value = (value or '').strip()
        if required and not value:
            raise ValueError(f'Preencha {label}.')
        if len(value) > limit:
            raise ValueError(f'{label}: máximo de {limit} caracteres.')
        return value

    @staticmethod
    def number(value):
        try:
            number = int(value)
        except (TypeError, ValueError):
            raise ValueError('Selecione um registro válido.')
        if number <= 0:
            raise ValueError('Selecione um registro válido.')
        return number

    @staticmethod
    def money(value):
        try:
            amount = Decimal(str(value).strip().replace(',', '.'))
            if not amount.is_finite() or amount < 0 or amount > Decimal('99999999.99'):
                raise ValueError('Orçamento fora do intervalo permitido.')
            if amount != amount.quantize(Decimal('0.01')):
                raise ValueError('Use no máximo duas casas decimais.')
            return int(amount * 100)
        except (InvalidOperation, TypeError):
            raise ValueError('Informe o orçamento como 150,00 ou 150.00, sem R$.')

    def save_client(self, data):
        name = self.text(data.get('name'), 'nome', required=True)
        phone = self.text(data.get('phone'), 'telefone', 50)
        email = self.text(data.get('email'), 'e-mail', 200)
        if email and ('@' not in email or '.' not in email.split('@')[-1]):
            raise ValueError('Informe um e-mail válido ou deixe vazio.')
        client_id = data.get('id')
        if client_id:
            client_id = self.number(client_id)
            if not self.repo.one('SELECT id FROM clients WHERE id=?', (client_id,)):
                raise ValueError('Cliente não encontrado.')
            self.repo.execute('UPDATE clients SET name=?, phone=?, email=? WHERE id=?', (name, phone, email, client_id))
            return client_id
        return self.repo.execute('INSERT INTO clients(name,phone,email) VALUES(?,?,?)', (name, phone, email))

    def create_equipment(self, data):
        client_id = self.number(data.get('client_id'))
        if not self.repo.one('SELECT id FROM clients WHERE id=?', (client_id,)):
            raise ValueError('Cliente não encontrado.')
        kind = self.text(data.get('kind'), 'tipo do equipamento', required=True)
        brand = self.text(data.get('brand'), 'marca/modelo')
        serial = self.text(data.get('serial'), 'número de série')
        return self.repo.execute('INSERT INTO equipment(client_id,kind,brand,serial) VALUES(?,?,?,?)', (client_id, kind, brand, serial))

    def create_order(self, data):
        equipment_id = self.number(data.get('equipment_id'))
        if not self.repo.one('SELECT id FROM equipment WHERE id=?', (equipment_id,)):
            raise ValueError('Equipamento não encontrado.')
        problem = self.text(data.get('problem'), 'defeito relatado', 3000, True)
        technician = self.text(data.get('technician'), 'técnico')
        return self.repo.create_order(equipment_id, problem, technician)

    def update_order(self, order_id, data):
        order_id = self.number(order_id)
        old = self.repo.order(order_id)
        if old is None:
            raise ValueError('Ordem de serviço não encontrada.')
        diagnosis = self.text(data.get('diagnosis'), 'diagnóstico', 3000)
        technician = self.text(data.get('technician'), 'técnico')
        cents = self.money(data.get('budget', '0'))
        approval = data.get('approval', 'Pendente')
        status = data.get('status', 'Aberta')
        if approval not in APPROVALS or status not in STATUSES:
            raise ValueError('Status ou aprovação inválidos.')
        if old['status'] in ('Entregue', 'Cancelada'):
            raise ValueError('Esta ordem está encerrada e não pode ser alterada.')
        if status in ('Aguardando aprovação', 'Em reparo', 'Concluída', 'Entregue') and not diagnosis:
            raise ValueError('Registre o diagnóstico antes de avançar.')
        if status in ('Em reparo', 'Concluída', 'Entregue') and approval != 'Aprovado':
            raise ValueError('O orçamento precisa estar aprovado para reparar, concluir ou entregar.')
        if status in ('Em reparo', 'Concluída', 'Entregue') and not technician:
            raise ValueError('Informe o técnico responsável.')
        if status == 'Entregue' and old['status'] != 'Concluída':
            raise ValueError('Primeiro salve como Concluída; depois registre a entrega.')
        if old['approval'] == 'Aprovado' and (cents != old['budget_cents'] or diagnosis != old['diagnosis']) and approval == 'Aprovado':
            raise ValueError('Orçamento ou diagnóstico alterado: salve com aprovação Pendente e solicite nova aprovação.')
        self.repo.update_order(order_id, technician, diagnosis, cents, approval, status)
