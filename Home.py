import random
import threading
import time

from flask import Flask, render_template

app = Flask(__name__)


class Ambiente:
    def __init__(self):
        self.computadores = []

    def adicionar_computador(self, computador):
        self.computadores.append(computador)

    def verificar_status(self):
        for computador in self.computadores:
            computador.verificar_componentes()

    def mostrar_status(self):
        status = []
        for computador in self.computadores:
            comp_status = {
                "id": computador.id,
                "componentes": [
                    {
                        "nome": componente.nome,
                        "vida": componente.tempo_vida,
                        "estado": componente.estado
                    } for componente in computador.componentes
                ]
            }
            status.append(comp_status)
        return status


class Computador:
    def __init__(self, id):
        self.id = id
        self.componentes = [
            Componente("Placa mãe", 50),
            Componente("Processador", 40),
            Componente("Memória RAM", 20),
            Componente("Armazenamento", 30),
            Componente("Fonte de alimentação", 35)
        ]
        self.funcionando = True

    def verificar_componentes(self):
        if not self.funcionando:
            return

        for componente in self.componentes:
            componente.degradar()
            if componente.estado == "quebrado":
                self.funcionando = False
                break

    def consertar(self):
        for componente in self.componentes:
            if componente.estado == "quebrado":
                componente.reparar()
        self.funcionando = True


class Componente:
    def __init__(self, nome, vida_maxima):
        self.nome = nome
        self.tempo_vida = vida_maxima
        self.estado = "funcionando"

    def degradar(self):
        if self.estado == "funcionando":
            self.tempo_vida -= 1
            if self.tempo_vida <= 0:
                self.estado = "quebrado"

    def reparar(self):
        self.tempo_vida = random.randint(5, 15)
        self.estado = "funcionando"


class Manutencao:
    @staticmethod
    def realizar_manutencao(computador):
        computador.consertar()


# Configuração do ambiente
ambiente = Ambiente()
for i in range(3):
    ambiente.adicionar_computador(Computador(i))


@app.route("/")
def index():
    status = ambiente.mostrar_status()
    return render_template("index.html", status=status)


def simular_ciclos():
    ciclo = 0
    while True:
        ciclo += 1
        print(f"Ciclo {ciclo}")
        ambiente.verificar_status()
        for computador in ambiente.computadores:
            if not computador.funcionando:
                Manutencao.realizar_manutencao(computador)
        time.sleep(10)


# Inicia a simulação em uma thread separada
threading.Thread(target=simular_ciclos, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)
