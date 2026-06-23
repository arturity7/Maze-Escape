<div align="center">

# 🦇 MAZE ESCAPE

### *eco-localização · labirinto · fuga*

Um labirinto completamente às escuras. Sua única arma é o som.

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow)
![Pygame](https://img.shields.io/badge/pygame--ce-✓-green)
![Licença acadêmica](https://img.shields.io/badge/uso-acadêmico-lightgrey)

</div>

---

## 🕹️ Sobre o jogo

**Maze Escape** é um jogo 2D desenvolvido em **Python + Pygame** como projeto final da disciplina de Introdução a Algoritmos/Programação.

A ideia é simples de explicar e difícil de dominar: você está preso em um labirinto onde **as paredes são invisíveis**. A única forma de "ver" o caminho é emitindo um pulso de **eco-localização** — uma onda sonora que se expande pelo mapa e revela, por alguns instantes, os trechos de parede e a saída que ela atravessa. Memorize o layout, ande no escuro, ecoe de novo, repita — até encontrar a saída.

<p align="center">
  <img src="docs/screenshots/menu-inicial.png" alt="Menu inicial do Maze Escape" width="700">
  <br>
  <em>Menu inicial — ajuste de volume, brilho e acesso rápido ao jogo</em>
</p>

<p align="center">
  <img src="docs/screenshots/gameplay-ecolocalizacao.png" alt="Gameplay mostrando o pulso de eco-localização revelando as paredes" width="700">
  <br>
  <em>Em jogo — o pulso de eco-localização "iluminando" as paredes próximas</em>
</p>

---

## 👥 Integrantes do grupo

- Arthur Gabriel
- Erick Calixto
- Crispim Bruno
- Lukas Nathan

---

## ✨ Funcionalidades

- 🌑 **Labirinto às escuras** — paredes só aparecem quando reveladas pela eco-localização.
- 📡 **Eco-localização** — pressione `E` (ou `Enter` do numpad para o Jogador 2) para emitir uma onda sonora que revela paredes e a saída próximas, com efeito visual de "pulso" e som.
- 🏃 **Três velocidades de movimento** — andar, correr (`Shift`) e *sprint* com brilho extra e cooldown (`Q` / `0` do numpad).
- 🎮 **Modo 1 ou 2 jogadores** — pressione `9` durante a partida para adicionar o Jogador 2 no mesmo teclado.
- 🖼️ **Personagens animados** — sprites com animação direcional (cima, baixo, esquerda, direita) para cada modo de movimento.
- 🎵 **Trilha sonora e efeitos** — música ambiente em loop e sons variados de eco.
- 🖥️ **Menu inicial interativo** — sliders de volume e brilho, tela cheia (`F11`) e tela de comandos antes da partida.
- 📷 **Câmera dinâmica** — segue o(s) jogador(es) ativo(s) pelo mapa, que é maior que a tela.
- 🏁 **Tela de vitória** — exibida ao alcançar a saída, com opção de jogar novamente.

---

## 🎯 Objetivo

Atravessar o labirinto e alcançar a **saída** (marcada em verde quando revelada pela eco-localização), usando o menor número possível de pulsos de eco e o mínimo de "tentativa e erro" contra as paredes invisíveis.

O jogo termina quando:
- um dos jogadores alcança a saída (vitória); ou
- o jogador fecha a janela manualmente.

---

## 🎮 Controles

### Jogador 1
| Tecla | Ação |
|---|---|
| `W` `A` `S` `D` | Mover |
| `Shift` esquerdo | Correr |
| `Q` | Sprint (rajada de velocidade + brilho, cooldown de 2s) |
| `E` | Emitir eco-localização |

### Jogador 2 *(opcional — pressione `9` para ativar)*
| Tecla | Ação |
|---|---|
| `↑ ↓ ← →` | Mover |
| `Shift` direito | Correr |
| `0` (numpad) | Sprint |
| `Enter` (numpad) | Emitir eco-localização |

### Geral
| Tecla | Ação |
|---|---|
| `9` | Adicionar Jogador 2 à partida |
| `F11` | Alternar tela cheia |
| `-` / `=` | Diminuir / aumentar volume da música |
| `ENTER` / `ESPAÇO` | Reiniciar após vencer |

> 💡 Os mesmos controles aparecem em jogo na **tela de comandos**, exibida automaticamente antes de cada partida.

---

## 🗺️ Estrutura do projeto

```
Maze-Escape/
├── main.py                  # Ponto de entrada da aplicação
├── requirements.txt         # Dependências (pygame-ce, pytest)
├── src/
│   ├── jogo.py               # Loop principal, menu, eco-localização, renderização
│   ├── config.py             # Constantes globais (tela, cores, caminhos)
│   ├── funcoes.py            # Funções auxiliares (ex.: carregar mapa)
│   ├── sprites.py            # Recorte e tratamento de spritesheets
│   └── dados.py               # Leitura/gravação de dados persistentes
├── assets/
│   ├── imagens/               # Spritesheets dos personagens e mapa
│   ├── sons/                  # Trilha sonora e efeitos de eco
│   └── fontes/                # Fontes tipográficas
├── data/                     # Arquivos persistentes (recorde/ranking)
├── tests/                    # Testes automatizados (pytest)
└── docs/                     # Documentação e proposta do projeto
```

---

## 🚀 Como executar o projeto

### Pré-requisitos
- Python **3.10+**
- `pip` instalado

### 1. Clonar o repositório

```bash
git clone https://github.com/arturity7/Maze-Escape.git
cd Maze-Escape
```

### 2. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 3. Executar o jogo

```bash
python src/jogo.py
```

> ⚠️ **Nota:** o `main.py` é o ponto de entrada planejado do projeto, mas a versão atual do loop de jogo está implementada diretamente em `src/jogo.py`. Por isso, rode esse arquivo diretamente para jogar. Ajustar `main.py`/`src/jogo.py` para que `python main.py` funcione de ponta a ponta é um bom próximo passo de refatoração.

---

## 🧪 Como executar os testes

```bash
python -m pytest
```

> Os testes em `tests/test_logica.py` cobrem funções de regra de jogo (pontuação, condição de derrota, limites de valores). Como o jogo evoluiu bastante desde a versão inicial do template, alguns testes podem precisar ser atualizados para refletir as funções atuais em `src/funcoes.py`.

---

## 🛠️ Tecnologias utilizadas

- [Python 3](https://www.python.org/)
- [Pygame Community Edition (pygame-ce)](https://pyga.me/)
- [pytest](https://docs.pytest.org/) para testes automatizados

---

## 📌 Roadmap / possíveis melhorias futuras

- [ ] Inimigos (morcegos) que reagem ao som do jogador — já há uma classe `Morcego` esboçada no código.
- [ ] Sistema de pontuação por número de ecos utilizados.
- [ ] Ranking/recorde persistente entre partidas (estrutura em `src/dados.py` já preparada).
- [ ] Diferentes mapas/níveis de dificuldade.
- [ ] Corrigir o ponto de entrada (`main.py`) para iniciar o jogo via `executar_jogo()`.

---

<div align="center">

*Projeto acadêmico desenvolvido para a disciplina de Introdução a Algoritmos/Programação.*

</div>
