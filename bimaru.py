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
        self.board.fill_blocked()
        self.id = BimaruState.state_id
        BimaruState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    def result(self, action):
        return BimaruState(self.board.place_ship(action[0], action[1]))

    def actions(self):
        return self.board.actions()

    # TODO: outros metodos da classe


class Board:
    """Representação interna de um tabuleiro de Bimaru."""

    def __init__(self, columns: list, rows: list, contents: list) -> None:
        self.columns = columns
        self.rows = rows
        self.contents = contents

    def __str__(self) -> str:
        return "\n".join(map(" ".join, self.contents))

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        if row < 0 or row > 9 or col < 0 or col > 9:
            return "."
        if self.contents[row][col] == "W":
            return "."
        return self.contents[row][col].lower()

    def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""
        return (self.get_value(row - 1, col), self.get_value(row + 1, col))

    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""
        return (self.get_value(row, col - 1), self.get_value(row, col + 1))

    def fill_row(self, row: int):
        self.contents[row] = [
            "." if self.contents[row][i] == "0" else self.contents[row][i]
            for i in range(10)
        ]

    def fill_col(self, col: int):
        for row in self.contents:
            if row[col] == "0":
                row[col] = "."

    def fill_tile(self, row: int, col: int):
        if self.get_value(row, col) == "0":
            self.contents[row][col] = "."

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
        self.fill_tile(row + 1, col)

    def fill_blocked_bottom(self, row: int, col: int):
        self.fill_vertical(row, col)
        self.fill_tile(row - 1, col)

    def fill_blocked_left(self, row: int, col: int):
        self.fill_horizontal(row, col)
        self.fill_tile(row, col - 1)

    def fill_blocked_right(self, row: int, col: int):
        self.fill_horizontal(row, col)
        self.fill_tile(row, col + 1)

    def fill_blocked_middle(self, row: int, col: int):
        vertical = self.adjacent_vertical_values(row, col)
        horizontal = self.adjacent_horizontal_values(row, col)

        if horizontal[0] == "." or horizontal[1] == ".":
            self.fill_vertical(row, col)
        elif vertical[0] == "." or vertical[1] == ".":
            self.fill_horizontal(row, col)
        elif horizontal[0] != "0" or horizontal[1] != "0":
            self.fill_horizontal(row, col)
        elif vertical[0] != "0" or vertical[1] != "0":
            self.fill_vertical(row, col)

    def fill_blocked(self):
        for i in range(10):
            if self.rows[i] == 0:
                self.fill_row(i)
            if self.columns[i] == 0:
                self.fill_col(i)

        for i in range(10):
            for j in range(10):
                tile = self.get_value(i, j)
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

    def place_ship(self, start: list, end: list):
        contents = [[tile for tile in row] for row in self.contents]
        rows = [value for value in self.rows]
        columns = [value for value in self.columns]

        if start[0] == end[0] and start[1] == end[1]:
            contents[start[0]][start[1]] = "c"
        elif start[0] == end[0]:
            contents[start[0]][start[1]] = "l"
            for i in range(start[1] + 1, end[1]):
                contents[start[0]][i] = "m"
            contents[start[0]][end[1]] = "r"
        elif start[1] == end[1]:
            contents[start[0]][start[1]] = "t"
            for i in range(start[0] + 1, end[0]):
                contents[i][start[1]] = "m"
            contents[end[0]][start[1]] = "b"

        return Board(columns, rows, contents)

    def actions(self):
        actions = []

        for i in range(10):
            # Rows
            j = 0
            while j != 10:
                while j != 10 and (
                    self.get_value(i, j) == "." or self.get_value(i, j) != "l"
                ):
                    j += 1
                if j == 10:
                    break

                k = j
                while (
                    k != 10
                    and k - j != 4
                    and (
                        self.get_value(i, k) == "0"
                        or self.get_value(i, k) == "r"
                        or self.get_value(i, k) == "m"
                    )
                ):
                    actions.append([[i, j], [i, k]])
                    k += 1

                j += 1
                if self.get_value(i, j) == "l":
                    j += 1

            # Columns
            j = 0
            while j != 10:
                while j != 10 and (
                    self.get_value(i, j) == "." or self.get_value(i, j) != "t"
                ):
                    j += 1
                if j == 10:
                    break

                k = j
                while (
                    k != 10
                    and k - j != 4
                    and (
                        self.get_value(i, j) == "0"
                        or self.get_value(i, j) == "b"
                        or self.get_value(i, k) == "m"
                    )
                ):
                    actions.append([[j, i], [k, i]])
                    k += 1

                j += 1
                if self.get_value(i, j) == "t":
                    j += 1

        return actions

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
        columns = list(map(int, lines[0].split()[1:]))
        rows = list(map(int, lines[1].split()[1:]))
        hints = [line.split()[1:] for line in lines[3:]]

        contents = [["0" for _ in columns] for _ in rows]
        for hint in hints:
            row = int(hint[0])
            col = int(hint[0])
            contents[row][col] = hint[2]
            if hint[2] != "W":
                rows[row] -= 1
                columns[col] -= 1

        return Board(columns, rows, contents)


class Bimaru(Problem):
    def __init__(self, initial: BimaruState):
        """O construtor especifica o estado inicial."""
        super().__init__(initial)

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
    print("\n")
    print(board.actions())
    # TODO:
    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
