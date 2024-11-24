import random
import threading
import time

from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Problemas específicos para cada componente
PROBLEMAS_COMPONENTES = {
    "Placa mãe": [
        ("Circuito queimado", 300, "Substituição do circuito danificado"),
        ("Conexão com a RAM falhou", 150, "Reparo nos slots de RAM"),
        ("BIOS corrompida", 200, "Reinstalação ou atualização do BIOS")
    ],
    "Processador": [
        ("Superaquecimento", 250, "Substituição do cooler ou aplicação de pasta térmica"),
        ("Pinos danificados", 400, "Troca do processador"),
        ("Falha na execução de instruções", 350, "Reconfiguração do processador")
    ],
    "Memória RAM": [
        ("Falha em um módulo", 100, "Troca do módulo de memória"),
        ("Erro de paridade", 120, "Reparo na memória"),
        ("Conexão instável com a placa-mãe", 150, "Ajuste nos conectores")
    ],
    "Armazenamento": [
        ("Setores defeituosos", 200, "Reparação de setores ou clonagem de disco"),
        ("Controlador de disco com defeito", 250, "Troca do controlador"),
        ("Desgaste do SSD", 300, "Substituição do SSD")
    ],
    "Fonte de alimentação": [
        ("Falta de energia", 150, "Substituição de capacitores"),
        ("Sobrecarga", 180, "Reparo no circuito interno"),
        ("Capacitor queimado", 200, "Troca do capacitor")
    ]
}


class Componente:
    def __init__(self, nome, vida_maxima, id_componente):
        self.id = id_componente  # Garantir que cada componente tenha um ID único
        self.nome = nome
        self.tempo_vida = vida_maxima
        self.estado = "funcionando"
        self.problema = None  # Para armazenar o problema específico quando quebrar
        self.aviso_manutencao = False

    def degradar(self):
        if self.estado == "funcionando":
            self.tempo_vida -= 1
            if self.tempo_vida <= 0:
                self.estado = "quebrado"
                self.problema = random.choice(PROBLEMAS_COMPONENTES[self.nome])

            if self.tempo_vida == 3 and not self.aviso_manutencao:
                self.aviso_manutencao = True  # Ativa o aviso quando os ciclos chegam a 3

    def reparar(self):
        self.tempo_vida = random.randint(5, 15)
        self.estado = "funcionando"
        self.problema = None  # Remove o problema após o reparo


class Computador:
    def __init__(self, id):
        self.id = id
        self.componentes = [
            Componente("Placa mãe", random.randint(5, 10), f"{id}-mãe"),
            Componente("Processador", random.randint(
                5, 10), f"{id}-processador"),
            Componente("Memória RAM", random.randint(5, 10), f"{id}-ram"),
            Componente("Armazenamento", random.randint(
                5, 10), f"{id}-armazenamento"),
            Componente("Fonte de alimentação",
                       random.randint(5, 10), f"{id}-fonte")
        ]
        self.funcionando = True

    def verificar_componentes(self):
        """Verifica todos os componentes e atualiza o estado do computador."""
        for componente in self.componentes:
            componente.degradar()
            if componente.estado == "quebrado":
                self.funcionando = False
                return  # Para imediatamente, pois o computador já está quebrado

    def consertar(self):
        """Conserta componentes quebrados e reativa o computador."""
        for componente in self.componentes:
            if componente.estado == "quebrado":
                componente.reparar()
        self.funcionando = True


class Manutencao:

    @staticmethod
    def buscar_componente_por_id(ambiente, componente_id):
        """Busca um componente específico em todos os computadores do ambiente."""
        for computador in ambiente.computadores:
            for componente in computador.componentes:
                if componente.id == componente_id:  # Compara com o ID real do componente
                    return computador, componente
        return None, None

    @staticmethod
    def realizar_manutencao_preventiva(ambiente, componente_id):
        """Realiza a manutenção preventiva em um componente específico."""
        computador, componente = Manutencao.buscar_componente_por_id(
            ambiente, componente_id)

        if componente:
            componente.tempo_vida += random.randint(10, 20)
            componente.estado = "funcionando"
            componente.aviso_manutencao = False
            return True
        else:
            return False

    @staticmethod
    def realizar_manutencao(computador):
        """Realiza a manutenção corretiva de um computador."""
        computador.consertar()

    @staticmethod
    def calcular_custo(conserto):
        _, custo, descricao = conserto
        return custo, descricao

    @staticmethod
    def obter_detalhes_problema(nome_componente):
        problemas = PROBLEMAS_COMPONENTES[nome_componente]
        problema, custo, conserto = random.choice(problemas)
        return problema, custo, conserto


class Ambiente:
    def __init__(self):
        self.computadores = []
        self.historico_problemas = []  # Histórico global de problemas

    def adicionar_computador(self, computador):
        self.computadores.append(computador)

    def verificar_status(self):
        for computador in self.computadores:
            if computador.funcionando:  # Só verifica componentes de computadores funcionando
                for componente in computador.componentes:
                    estado_anterior = componente.estado
                    componente.degradar()
                    # Se o componente tiver 3 ciclos restantes
                    if componente.tempo_vida == 3:
                        # Adiciona a flag para mostrar aviso de manutenção
                        componente.aviso_manutencao = True
                    if estado_anterior == "funcionando" and componente.estado == "quebrado":
                        problema, custo, conserto = Manutencao.obter_detalhes_problema(
                            componente.nome)
                        self.registrar_problema(
                            computador.id, componente.nome, problema, custo, conserto)
                        computador.funcionando = False  # Para o computador imediatamente
                        break  # Sai do loop de componentes após detectar a falha

    def registrar_problema(self, computador_id, componente, problema, custo, conserto):
        self.historico_problemas.append({
            "computador_id": computador_id,
            "componente": componente,
            "problema": problema,
            "custo": custo,
            "conserto": conserto
        })

    def mostrar_historico_problemas(self):
        return self.historico_problemas

    def mostrar_status(self):
        status = []
        for computador in self.computadores:
            comp_status = {
                "id": computador.id,
                "componentes": [
                    {
                        "nome": componente.nome,
                        "vida": componente.tempo_vida,
                        "estado": componente.estado,
                        "aviso_manutencao": hasattr(componente, 'aviso_manutencao') and componente.aviso_manutencao
                    } for componente in computador.componentes
                ],
                "funcionando": computador.funcionando
            }
            status.append(comp_status)
        return status


# Configuração do ambiente
ambiente = Ambiente()
for i in range(3):
    ambiente.adicionar_computador(Computador(i))


@app.route('/manutencao_preventiva/<int:componente_id>', methods=['POST'])
def manutencao_preventiva(componente_id):
    if Manutencao.realizar_manutencao_preventiva(ambiente, componente_id):
        return jsonify({"success": True, "message": "Manutenção preventiva realizada com sucesso!"})
    return jsonify({"success": False, "message": "Componente não encontrado ou já em bom estado."})


@app.route("/")
def index():
    status = ambiente.mostrar_status()
    historico = ambiente.mostrar_historico_problemas()  # Adicionando o histórico
    return render_template("index.html", status=status, historico=historico)


@app.route("/consertar/<int:computador_id>", methods=["POST"])
def consertar(computador_id):
    if 0 <= computador_id < len(ambiente.computadores):
        computador = ambiente.computadores[computador_id]
        if not computador.funcionando:
            Manutencao.realizar_manutencao(computador)
        return jsonify(success=True)
    return jsonify(success=False, error="Computador não encontrado."), 404


@app.route("/adicionar", methods=["POST"])
def adicionar():
    novo_id = len(ambiente.computadores)
    ambiente.adicionar_computador(Computador(novo_id))
    return jsonify(success=True)


def simular_ciclos():
    ciclo = 0
    while True:
        ciclo += 1
        print(f"Ciclo {ciclo}")
        ambiente.verificar_status()
        time.sleep(10)


# Inicia a simulação em uma thread separada
threading.Thread(target=simular_ciclos, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)
