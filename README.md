# Nome do Jogo

Projeto final da disciplina de Introdução a Algoritmos/Programação, desenvolvido com Python e Pygame.

Este repositório é um template para os grupos da disciplina. A proposta é começar com uma base funcional e evoluir o jogo ao longo do semestre.

## Integrantes do grupo

- Arthur Gabriel
- Erick Calixto
- Crispim Bruno


## Estrutura do projeto

- `main.py`: ponto de entrada da aplicação.
- `src/`: código-fonte principal do jogo (loop, regras, sprites e dados).
- `assets/`: imagens, fontes e sons.
- `data/`: arquivos persistentes (recorde/ranking).
- `tests/`: testes unitários com `pytest`.
- `docs/`: documentação do projeto, incluindo proposta inicial.

## Descrição do jogo

Conceito do Jogo

Maze Escape é um jogo desenvolvido em Python no qual o jogador deve explorar um labirinto e encontrar a saída antes de ficar preso. O desafio principal consiste em navegar pelo mapa utilizando raciocínio lógico e percepção espacial para descobrir o caminho correto.

O jogo será executado em terminal e terá foco na aplicação prática dos conceitos estudados na disciplina, como estruturas de dados, funções, matrizes, manipulação de arquivos e controle de fluxo.

Principais Elementos do Jogo

O jogo será composto pelos seguintes elementos:

Jogador controlado pelo teclado.
Labirinto formado por paredes e caminhos livres.
Ponto inicial do mapa.
Saída do labirinto.
Sistema de movimentação.
Contador de movimentos.
Diferentes mapas carregados por arquivos.

Representação simplificada:

##########
#P # #

### #
# S#

##########

Onde:

P = Jogador
S = Saída




= Parede
Espaço vazio = Caminho livre


## Objetivo do jogador

Vitória

O jogador vence ao alcançar a saída do labirinto.

Derrota

Na versão mínima não haverá sistema de derrota.

Como funcionalidade futura, poderão ser adicionados:

Limite de tempo.
Armadilhas.
Inimigos.
Sistema de vidas.
Encerramento

O jogo será encerrado quando:

O jogador alcançar a saída.
O jogador escolher sair manualmente.


## Regras do jogo

O jogador inicia em uma posição definida no mapa.
Apenas movimentos válidos serão permitidos.
Não será possível atravessar paredes.
O jogador deverá encontrar a saída do labirinto.
Cada movimento será contabilizado.
O jogo poderá possuir diferentes níveis de dificuldade através de mapas distintos.

## Controles

Os controles serão realizados pelo teclado:

W → mover para cima
S → mover para baixo
A → mover para a esquerda
D → mover para a direita
Q → sair do jogo

## Como executar o projeto

### 1. Clonar o repositório

```bash
git clone LINK_DO_REPOSITORIO
cd NOME_DA_PASTA
pip install -r requirements.txt
python main.py
```

## Como executar os testes

```bash
python -m pytest
```

## Checklist mínimo para entrega

- Preencher este README com nome final, descrição real, regras e controles do jogo.
- Atualizar `docs/proposta.MD` com a proposta do grupo.
- Garantir que o jogo executa com `python main.py`.
- Garantir que os testes passam com `pytest`.

## Observações para os alunos

- Mantenham o código organizado em módulos pequenos e com responsabilidade clara.
- Comentem partes importantes da lógica, principalmente regras do jogo.
- Registrem decisões técnicas no README do grupo ao longo do desenvolvimento.
