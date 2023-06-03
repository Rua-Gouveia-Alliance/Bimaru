# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 93:
# 102611 João Gouveia
# 102604 Gonçalo Rua

import sys
import numpy as np
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

    def __init__(self, board, ships):
        # setup board
        self.board = board
        board.fill_blocked()

        # remaining ships
        self.ships = ships

        # id
        self.id = BimaruState.state_id
        BimaruState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    def __str__(self) -> str:
        tiles = self.board.tiles.copy()
        for hint in self.board.hints:
            tiles[hint[0], hint[1]] = hint[2].upper()

        return "\n".join(map("".join, tiles))


class Board:
    """Representação interna de um tabuleiro de Bimaru."""

    def __init__(self, cols: list, rows: list, tiles: list, hints: list) -> None:
        self.cols = cols
        self.rows = rows
        self.tiles = tiles
        self.hints = hints

    def fill_row(self, row: int):
        self.tiles[row, :][self.tiles[row, :] == "0"] = "."

    def fill_col(self, col: int):
        self.tiles[:, col][self.tiles[:, col] == "0"] = "."

    def fill_blocked(self):
        for i in range(10):
            if self.cols[i] == 0:
                self.fill_col(i)

            if self.rows[i] == 0:
                self.fill_row(i)

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        return self.tiles[row, col]

    def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""
        return (self.tiles[row - 1, col], self.tiles[row + 1, col])

    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""
        return (self.tiles[row, col - 1], self.tiles[row, col + 1])

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
        tiles = np.full((10, 10), "0", dtype=str)
        convert = lambda x: (int(x[0]), int(x[1]), x[2].lower())
        hints = [convert(line.split()[1:]) for line in lines[3:]]

        return Board(columns, rows, tiles, hints)


class Bimaru(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        ships = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]
        super().__init__(BimaruState(board, ships))

    def get_combinations(self, array: list, n: int, el=[]) -> list:
        if len(el) == n:
            return [el]
        combinations = []
        for i in range(len(array)):
            new_el = el.copy()
            new_el.append(array[i])
            combinations += self.get_combinations(array[i + 1 :], n, new_el)
        return combinations

    def subtract_tiles(self, ship: list, rows: list, cols: list):
        start = ship[0]
        end = ship[1]
        if start[0] == end[0] and start[1] == end[1]:
            rows[start[0]] -= 1
            cols[start[1]] -= 1
        elif start[0] == end[0]:
            rows[start[0]] -= end[1] - start[1] + 1
            cols[start[1] : end[1] + 1] -= 1
        elif start[1] == end[1]:
            rows[start[0] : end[0] + 1] -= 1
            cols[start[1]] -= end[0] - start[0] + 1

    def overlap(self, ship1: list, ship2: list) -> bool:
        ship1_area = [
            [ship1[0][0] - 1, ship1[0][1] - 1],
            [ship1[1][0] + 1, ship1[1][1] + 1]
        ]

        ship2_area = [
            [ship2[0][0] - 1, ship2[0][1] - 1],
            [ship2[1][0] + 1, ship2[1][1] + 1]
        ]

        if ship1_area[1][0] < ship2_area[0][0] or ship1_area[0][0] > ship2_area[1][0]:
            return False
        if ship1_area[1][1] < ship2_area[0][1] or ship1_area[0][1] > ship2_area[1][1]:
            return False

        return True

    def remove_incompatible(self, state: BimaruState, actions: list) -> list:
        possible_actions = []
        action_count = len(actions)
        for action in actions:
            incompatible = False

            for i in range(action_count):
                for j in range(i + 1, action_count):
                    if self.overlap(action[i], action[j]):
                        incompatible = True
                        break
            if incompatible:
                pass

            rows = state.board.rows.copy()
            cols = state.board.cols.copy()
            for ship in action:
                self.subtract_tiles(ship, rows, cols)

            for i in range(10):
                if rows[i] < 0 or cols[i] < 0:
                    incompatible = True

            if incompatible:
                pass

            possible_actions.append(action)

        return possible_actions

    def possible_ships(
        self, tiles: list, max_ships: int, target_size: int, create_action
    ) -> list:
        ships = []
        for j in range(10):
            if tiles[j] == "0":
                k = j
                size = 1
                while k < 10 and tiles[k] == "0" and size <= target_size:
                    if size <= max_ships and size == target_size:
                        ships.append(create_action(j, k))
                    size += 1
                    k += 1
        return ships

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        if not state.ships:
            return []

        ships = []
        board = state.board
        tiles = state.board.tiles
        target_size = max(state.ships)
        ship_amount = state.ships.count(target_size)

        for hint in state.board.hints:
            if hint[2] == "w":
                if tiles[hint[0], hint[1]] != "." and tiles[hint[0], hint[1]] != "0":
                    return []
            elif tiles[hint[0], hint[1]] != hint[2] and tiles[hint[0], hint[1]] != "0":
                return []

        for i in range(10):
            horz = lambda j, k: [[i, j], [i, k]]
            ships += self.possible_ships(tiles[i], board.rows[i], target_size, horz)
            vert = lambda j, k: [[j, i], [k, i]]
            ships += self.possible_ships(tiles[:, i], board.cols[i], target_size, vert)

        if target_size == 4:
            return ships

        combinations = self.get_combinations(ships, ship_amount)
        actions = self.remove_incompatible(combinations)

        return actions

    def fill_ship_area(self, tiles: list, action: list):
        start = action[0]
        end = action[1]

        min_col = max(start[1] - 1, 0)
        min_row = max(start[0] - 1, 0)
        max_col = min(end[1] + 1, 9)
        max_row = min(end[0] + 1, 9)

        tiles[min_row : max_row + 1, min_col : max_col + 1] = "."

    def result(self, state: BimaruState, action: list):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        tiles = state.board.tiles.copy()
        rows = state.board.rows.copy()
        cols = state.board.cols.copy()
        ships = state.ships.copy()

        for ship in action:
            start = ship[0]
            end = ship[1]
            self.subtract_tiles(ship, rows, cols)
            self.fill_ship_area(tiles, action)

            if start[0] == end[0] and start[1] == end[1]:
                tiles[start[0], start[1]] = "c"
                ships.remove(1)

            elif start[0] == end[0]:
                tiles[start[0], start[1]] = "l"
                tiles[start[0], start[1] + 1 : end[1]] = "m"
                tiles[end[0], end[1]] = "r"

                ships.remove(end[1] - start[1] + 1)

            elif start[1] == end[1]:
                tiles[start[0], start[1]] = "t"
                tiles[start[0] + 1 : end[0], start[1]] = "m"
                tiles[end[0], end[1]] = "b"

                ships.remove(end[0] - start[0] + 1)

        new_board = Board(cols, rows, tiles, state.board.hints)
        return BimaruState(new_board, ships)

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""

        tiles = state.board.tiles
        hints = state.board.hints

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
    input_board = Board.parse_instance()
    problem = Bimaru(input_board)
    solution = depth_first_tree_search(problem)
    if solution is not None:
        print(solution.state)
