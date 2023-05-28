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

    def __init__(self, board, available_sizes):
        self.board = board
        self.available_sizes = available_sizes
        try:
            self.board.fill_blocked(self.available_sizes)
        except:
            self.available_sizes = []
        self.id = BimaruState.state_id
        BimaruState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    def __str__(self) -> str:
        return self.board.__str__()

    def get_board(self) -> list:
        return self.board

    def get_available_sizes(self) -> list:
        return self.available_sizes

    def result(self, action):
        sizes = [size for size in self.available_sizes]
        if action[0][0] == action[1][0]:
            sizes.remove(action[1][1] - action[0][1] + 1)
        else:
            sizes.remove(action[1][0] - action[0][0] + 1)

        return BimaruState(self.board.place_ship(action[0], action[1]), sizes)

    def actions(self) -> list:
        if not self.available_sizes:
            return []
        return self.board.actions(self.available_sizes)

    # TODO: outros metodos da classe


class Board:
    """Representação interna de um tabuleiro de Bimaru."""

    def __init__(self, columns: list, rows: list, contents: list) -> None:
        self.columns = columns
        self.rows = rows
        self.contents = contents

    def __str__(self) -> str:
        # return "\n".join(map(" ".join, self.contents))
        string = ""
        for i in range(10):
            string += " ".join(self.contents[i]) + " " + str(self.rows[i]) + "\n"
        cols = map(str, self.columns)
        string += " ".join(cols) + "\n"
        return string

    def row_value(self, row):
        return self.rows[row]

    def column_value(self, col):
        return self.columns[col]

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

    def fill_blocked(self, available_sizes):
        free_spots_rows = [0 for _ in range(10)]
        free_spots_cols = [0 for _ in range(10)]

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
                elif tile == "0":
                    free_spots_rows[i] += 1
                    free_spots_cols[j] += 1

        for i in range(10):
            if free_spots_rows[i] == self.rows[i]:
                j = 0
                while j != 10:
                    while (
                        self.get_value(i, j) != "0"
                        and self.get_value(i, j) != "l"
                        and j != 10
                    ):
                        j += 1
                    if j == 10:
                        break

                    k = j
                    while self.get_value(i, k) == "0" or self.get_value(i, k) == "r":
                        k += 1
                    k -= 1
                    if k - j != 0:
                        self.place_ship([i, j], [i, k])
                        available_sizes.remove(k - j + 1)
                    j = k + 1

            if free_spots_cols[i] == self.columns[i]:
                j = 0
                while j != 10:
                    while (
                        self.get_value(j, i) != "0"
                        and self.get_value(j, i) != "t"
                        and j != 10
                    ):
                        j += 1
                    if j == 10:
                        break

                    k = j
                    while self.get_value(k, i) == "0" or self.get_value(k, i) == "b":
                        k += 1
                    k -= 1
                    if k - j != 0:
                        self.place_ship([j, i], [k, i])
                        available_sizes.remove(k - j + 1)
                    j = k + 1

            if self.rows[i] == 0:
                self.fill_row(i)

            if self.columns[i] == 0:
                self.fill_col(i)

    def place_ship(self, start: list, end: list):
        contents = [[tile for tile in row] for row in self.contents]
        rows = [value for value in self.rows]
        columns = [value for value in self.columns]

        if start[0] == end[0] and start[1] == end[1]:
            contents[start[0]][start[1]] = "c"
            rows[start[0]] -= 1
            columns[start[1]] -= 1
        elif start[0] == end[0]:
            contents[start[0]][start[1]] = "l"
            rows[start[0]] -= 1
            columns[start[1]] -= 1
            for i in range(start[1] + 1, end[1]):
                contents[start[0]][i] = "m"
                rows[start[0]] -= 1
                columns[i] -= 1
            contents[end[0]][end[1]] = "r"
            rows[end[0]] -= 1
            columns[end[1]] -= 1
        elif start[1] == end[1]:
            contents[start[0]][start[1]] = "t"
            rows[start[0]] -= 1
            columns[start[1]] -= 1
            for i in range(start[0] + 1, end[0]):
                contents[i][start[1]] = "m"
                rows[i] -= 1
                columns[start[1]] -= 1
            contents[end[0]][end[1]] = "b"
            rows[end[0]] -= 1
            columns[end[1]] -= 1
        return Board(columns, rows, contents)

    def actions(self, available_sizes):
        actions = []

        for i in range(10):
            # Rows
            j = 0
            while j != 10:
                while (
                    j != 10
                    and self.get_value(i, j) != "0"
                    and self.get_value(i, j) != "l"
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
                    size = k - j + 1
                    if size in available_sizes and self.rows[i] - size > -1:
                        actions.append([[i, j], [i, k]])
                    k += 1

                j += 1
                if self.get_value(i, j) == "l":
                    j += 1

            # Columns
            j = 0
            while j != 10:
                while (
                    j != 10
                    and self.get_value(i, j) != "t"
                    and self.get_value(i, j) != "0"
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
                    size = k - j + 1
                    if size in available_sizes and self.columns[i] - size > -1:
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
        rows = list(map(int, lines[0].split()[1:]))
        columns = list(map(int, lines[1].split()[1:]))
        hints = [line.split()[1:] for line in lines[3:]]

        contents = [["0" for _ in columns] for _ in rows]
        for hint in hints:
            contents[int(hint[0])][int(hint[1])] = hint[2]

        return Board(columns, rows, contents)


class Bimaru(Problem):
    def __init__(self, initial: BimaruState):
        """O construtor especifica o estado inicial."""
        super().__init__(initial)

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        return state.actions()

    def result(self, state: BimaruState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        return state.result(action)

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        board = state.get_board()

        for i in range(10):
            if board.column_value(i) != 0 or board.row_value(i) != 0:
                return False

        return not not state.get_available_sizes()

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass

    # TODO: outros metodos da classe


if __name__ == "__main__":
    initial_sizes = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]
    board = Board.parse_instance()
    state = BimaruState(board, initial_sizes)
    problem = Bimaru(state)
    solution = breadth_first_tree_search(problem)
    print(solution.state)
    """
    initial_sizes = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]
    board = Board.parse_instance()
    print(board)
    print("\n")
    state = BimaruState(board, initial_sizes)
    print(state)
    print("\n")
    print(state.actions()[0])
    print("\n")
    new_board = state.result(state.actions()[0])
    print(new_board)
    print("\n")
    """
