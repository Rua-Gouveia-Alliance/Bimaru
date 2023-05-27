# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 00000 Nome1
# 00000 Nome2

import sys
from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)


class BimaruState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = BimaruState.state_id
        BimaruState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    # TODO: outros metodos da classe


class Board:
    """Representação interna de um tabuleiro de Bimaru."""

    def __init__(self, columns: list, rows: list, board: list) -> None:
        self.columns = columns
        self.rows = rows
        self.board = board

    def __str__(self) -> str:
        return "\n".join(map(" ".join, self.board))

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        if row < 0 or row > 9 or col < 0 or col > 9:
            return "."
        return self.board[row][col]

    def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""
        return (self.get_value(row - 1, col), self.get_value(row + 1, col))

    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""
        return (self.get_value(row, col - 1), self.get_value(row, col + 1))

    def fill_row(self, row: int):
        self.board[row] = ["." for _ in range(10)]

    def fill_col(self, col: int):
        for row in self.board:
            row[col] = "."

    def fill_tile(self, row: int, col: int):
        if self.get_value(row, col) == "0":
            self.board[row][col] = "."

    def fill_vertical(self, row: int, col: int):
        for i in range(-1, 2, 2):
            self.fill_tile(row - 1, col + i)
            self.fill_tile(row, col + i)
            self.fill_tile(row + 1, col + i)

    def fill_horizontal(self, row: int, col: int):
        for i in range(-1, 2, 2):
            self.fill_tile(row + i, col - 1)
            self.fill_tile(row + i, col)
            self.fill_tile(row + i, col + 1)

    def fill_blocked_circle(self, row: int, col: int):
        self.fill_vertical(row, col)
        self.fill_horizontal(row, col)

    def fill_blocked_top(self, row: int, col: int):
        self.fill_vertical(row, col)
        self.fill_tile(row - 1, col)

    def fill_blocked_bottom(self, row: int, col: int):
        self.fill_vertical(row, col)
        self.fill_tile(row + 1, col)

    def fill_blocked_left(self, row: int, col: int):
        self.fill_horizontal(row, col)
        self.fill_tile(row, col - 1)

    def fill_blocked_right(self, row: int, col: int):
        self.fill_horizontal(row, col)
        self.fill_tile(row, col + 1)

    def fill_blocked_middle(self, row: int, col: int):
        if self.get_value(row, col - 1) != "0" or self.get_value(row, col + 1) != "0":
            self.fill_horizontal(row, col)
        if self.get_value(row - 1, col) != "0" or self.get_value(row + 1, col) != "0":
            self.fill_vertical(row, col)

    def fill_blocked(self):
        for i in range(10):
            if self.rows[i] == 0:
                self.fill_row(i)
            if self.columns[i] == 0:
                self.fill_col(i)

        for i in range(10):
            for j in range(10):
                tile = self.board[i][j].lower()

                if tile == "t":
                    self.fill_blocked_top(i, j)
                elif tile == "b":
                    self.fill_blocked_bottom(i, j)
                elif tile == "l":
                    self.fill_blocked_left(i, j)
                elif tile == "r":
                    self.fill_blocked_right(i, j)
                elif tile == "m":
                    self.fill_blocked_middle(i, j)
                elif tile == "c":
                    self.fill_blocked_circle(i, j)

    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.

        Por exemplo:
            $ python3 bimaru.py < input_T01

            > from sys import stdin
            > line = stdin.readline().split()
        """

        lines = sys.stdin.readlines()
        columns = lines[0].split()[1:]
        rows = lines[1].split()[1:]
        hints = [line.split()[1:] for line in lines[3:]]

        board = [["0" for _ in columns] for _ in rows]
        for hint in hints:
            board[int(hint[0])][int(hint[1])] = hint[2]

        return Board(columns, rows, board)


class Bimaru(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        # TODO
        pass

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        # TODO
        pass

    def result(self, state: BimaruState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        # TODO
        pass

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        # TODO
        pass

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass

    # TODO: outros metodos da classe


if __name__ == "__main__":
    board = Board.parse_instance()
    board.fill_blocked()
    print(board)
    # TODO:
    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
