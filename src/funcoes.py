import os

def carregar_mapa(caminho):
    pasta_atual = os.path.dirname(__file__)  # pasta do funcoes.py (src/)
    caminho_completo = os.path.join(pasta_atual, caminho)
    mapa = []
    with open(caminho_completo, "r") as f:
        for linha in f:
            mapa.append(list(linha.strip()))
    return mapa
