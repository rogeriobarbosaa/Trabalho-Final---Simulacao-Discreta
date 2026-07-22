import csv
import simpy

# Tempos fixos das operações de acordo com o porte da aeronave
TEMPOS = {
    "P": {"pouso": 40, "desembarque": 20, "hangar": 35, "embarque": 30, "decolagem": 40},
    "G": {"pouso": 60, "desembarque": 40, "hangar": 70, "embarque": 60, "decolagem": 60}
}

class Metricas:
    def __init__(self):
        self.espera_pouso = []
        self.espera_plat_desemb = []
        self.espera_hangar = []
        self.espera_plat_emb = []
        self.espera_decolagem = []
        self.termino = []

class Aviao:
    def __init__(self, env, id_aviao, tipo, chegada, rec, m):
        self.env = env
        self.id_aviao = id_aviao
        self.tipo = tipo
        self.chegada = chegada
        self.rec = rec
        self.m = m
        self.env.process(self.operar())

    def operar(self):
        # Aguarda o horário de chegada da aeronave
        yield self.env.timeout(self.chegada - self.env.now)
        
        t = TEMPOS[self.tipo]
        pista = self.rec["pista_p"] if self.tipo == "P" else self.rec["pista_g"]

        # 1. POUSO
        with pista.request() as req_pouso:
            t0 = self.env.now
            yield req_pouso
            self.m.espera_pouso.append(self.env.now - t0)
            yield self.env.timeout(t["pouso"])

        # 2. DESEMBARQUE (Requisita manualmente para segurar o recurso)
        req_plat_desemb = self.rec["plataforma"].request()
        t0 = self.env.now
        yield req_plat_desemb
        self.m.espera_plat_desemb.append(self.env.now - t0)
        yield self.env.timeout(t["desembarque"])

        # 3. HANGAR
        req_hangar = self.rec["hangar"].request()
        t0 = self.env.now
        yield req_hangar
        self.rec["plataforma"].release(req_plat_desemb) 
        self.m.espera_hangar.append(self.env.now - t0)
        yield self.env.timeout(t["hangar"])
        
        # CORREÇÃO: Hangar é liberado AQUI, antes de pedir a plataforma de embarque
        self.rec["hangar"].release(req_hangar)

        # 4. EMBARQUE
        req_plat_emb = self.rec["plataforma"].request()
        t0 = self.env.now
        yield req_plat_emb
        self.m.espera_plat_emb.append(self.env.now - t0)
        yield self.env.timeout(t["embarque"])

        # 5. DECOLAGEM
        with pista.request() as req_decolagem:
            t0 = self.env.now
            yield req_decolagem
            self.rec["plataforma"].release(req_plat_emb) 
            self.m.espera_decolagem.append(self.env.now - t0)
            yield self.env.timeout(t["decolagem"])

        self.m.termino.append(self.env.now)

def simular(csv_path, plataformas, hangares, pistas_p, pistas_g):
    env = simpy.Environment()
    
    rec = {
        "pista_p": simpy.Resource(env, capacity=pistas_p),
        "pista_g": simpy.Resource(env, capacity=pistas_g),
        "plataforma": simpy.Resource(env, capacity=plataformas),
        "hangar": simpy.Resource(env, capacity=hangares)
    }
    m = Metricas()

    with open(csv_path, 'r') as f:
        linhas = list(csv.DictReader(f))

    for linha in linhas:
        Aviao(env, linha["id"], linha["tipo"], float(linha["horario_chegada"]), rec, m)

    env.run()
    
    tf = max(m.termino)

    print(f"\n--- Cenário: plat={plataformas} hangares={hangares} pista_p={pistas_p} pista_g={pistas_g} ---")
    print(f"Tempo final da simulação: {tf} minutos")
    
    print(f"Fila Máxima (Pouso): {max(m.espera_pouso)} min")
    print(f"Fila Máxima (Desembarque): {max(m.espera_plat_desemb)} min")
    print(f"Fila Máxima (Hangar): {max(m.espera_hangar)} min")
    print(f"Fila Máxima (Embarque): {max(m.espera_plat_emb)} min")
    print(f"Fila Máxima (Decolagem): {max(m.espera_decolagem)} min")

if __name__ == "__main__":
    arquivo = 'chegadas.csv'
    
    # 1. Cenário Base 
    simular(arquivo, plataformas=5, hangares=3, pistas_p=2, pistas_g=1)
    
    # 2. Cenários alternativos 
    simular(arquivo, plataformas=5, hangares=3, pistas_p=3, pistas_g=2)
    simular(arquivo, plataformas=7, hangares=5, pistas_p=3, pistas_g=2)
