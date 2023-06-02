# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 93:
# 102611 João Gouveia
# 102604 Gonçalo Rua

import sys
import numpy as np
from search import Problem, Node, breadth_first_tree_search, astar_search


class BimaruState:
    state_id = 0

    def __init__(self, board, ships):
        self.board = board
        self.ships = ships
        self.id = BimaruState.state_id
        BimaruState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    def __str__(self) -> str:
        tiles = Tiles(self.board.cols, self.board.rows, self.board.placed).tiles
        for hint in self.board.hints:
            tiles[hint[0], hint[1]] = hint[2].upper()

        return "\n".join(map("".join, tiles))


class Board:
    """Representação interna de um tabuleiro de Bimaru."""

    def __init__(self, cols: list, rows: list, placed: list, hints: list) -> None:
        self.cols = cols
        self.rows = rows
        self.placed = placed
        self.hints = hints

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
        rows = np.array(list(map(int, lines[0].split()[1:])))
        columns = np.array(list(map(int, lines[1].split()[1:])))
        convert = lambda x: (int(x[0]), int(x[1]), x[2].lower())
        hints = [convert(line.split()[1:]) for line in lines[3:]]

        return Board(columns, rows, [], hints)


class Tiles:
    def __init__(self, cols: list, rows: list, placed: list) -> None:
        self.tiles = np.full((10, 10), "0")
        self.fill_blocked(cols, rows)
        for ship in placed:
            self.draw(ship)

    def fill_row(self, row: int):
        self.tiles[row, :][self.tiles[row, :] == "0"] = "."

    def fill_col(self, col: int):
        self.tiles[:, col][self.tiles[:, col] == "0"] = "."

    def fill_blocked(self, cols: list, rows: list):
        for i in range(10):
            if cols[i] == 0:
                self.fill_col(i)

            if rows[i] == 0:
                self.fill_row(i)

    def fill_ship_area(self, action: list):
        start = action[0]
        end = action[1]

        min_col = max(start[1] - 1, 0)
        min_row = max(start[0] - 1, 0)
        max_col = min(end[1] + 1, 9)
        max_row = min(end[0] + 1, 9)

        self.tiles[min_row : max_row + 1, min_col : max_col + 1] = "."

    def draw(self, action: list):
        start = action[0]
        end = action[1]

        self.fill_ship_area(action)

        if start[0] == end[0] and start[1] == end[1]:
            self.tiles[start[0], start[1]] = "c"

        elif start[0] == end[0]:
            self.tiles[start[0], start[1]] = "l"
            self.tiles[start[0], start[1] + 1 : end[1]] = "m"
            self.tiles[end[0], end[1]] = "r"

        elif start[1] == end[1]:
            self.tiles[start[0], start[1]] = "t"
            self.tiles[start[0] + 1 : end[0], start[1]] = "m"
            self.tiles[end[0], end[1]] = "b"


class Bimaru(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        ships = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]
        super().__init__(BimaruState(board, ships))

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        actions = []
        board = state.board
        tiles = Tiles(state.board.cols, state.board.rows, state.board.placed).tiles
        target_size = max(state.ships)

        if not state.ships:
            return []

        for hint in state.board.hints:
            if hint[2] == "w":
                if tiles[hint[0], hint[1]] != "." and tiles[hint[0], hint[1]] != "0":
                    return []
            elif tiles[hint[0], hint[1]] != hint[2] and tiles[hint[0], hint[1]] != "0":
                return []

        for i in range(10):
            row = tiles[i]
            for j in range(10):
                if row[j] == "0":
                    k = j
                    size = k - j + 1
                    while k < 10 and row[k] == "0" and size <= target_size:
                        if size <= board.rows[i] and size == target_size:
                            actions.append([[i, j], [i, k]])
                        size += 1
                        k += 1

        for i in range(10):
            col = tiles[:, i]
            for j in range(10):
                if col[j] == "0":
                    k = j
                    size = k - j + 1
                    while k < 10 and col[k] == "0" and size <= target_size:
                        if size <= board.cols[i] and size == target_size:
                            actions.append([[j, i], [k, i]])
                        size += 1
                        k += 1

        return actions

    def result(self, state: BimaruState, action: list):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        start = action[0]
        end = action[1]

        placed = state.board.placed.copy()
        rows = state.board.rows.copy()
        cols = state.board.cols.copy()
        ships = state.ships.copy()

        placed.append(action)
        if start[0] == end[0] and start[1] == end[1]:
            rows[start[0]] -= 1
            cols[start[1]] -= 1
            ships.remove(1)

        elif start[0] == end[0]:
            rows[start[0]] -= end[1] - start[1] + 1
            cols[start[1] : end[1] + 1] -= 1
            ships.remove(end[1] - start[1] + 1)

        elif start[1] == end[1]:
            rows[start[0] : end[0] + 1] -= 1
            cols[start[1]] -= end[0] - start[0] + 1
            ships.remove(end[0] - start[0] + 1)

        new_board = Board(cols, rows, placed, state.board.hints)
        return BimaruState(new_board, ships)

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""

        hints = state.board.hints
        tiles = Tiles(state.board.cols, state.board.rows, state.board.placed).tiles

        for i in range(10):
            if state.board.rows[i] != 0 or state.board.cols[i] != 0:
                return False

        for hint in hints:
            if hint[2] == "w":
                if tiles[hint[0], hint[1]] != "." and tiles[hint[0], hint[1]] != "0":
                    return False
            elif tiles[hint[0], hint[1]] != hint[2]:
                return False

        return not state.ships


if __name__ == "__main__":
    board = Board.parse_instance()
    problem = Bimaru(board)
    solution = breadth_first_tree_search(problem)
    print(solution.state)
