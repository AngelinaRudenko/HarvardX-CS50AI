import itertools
import random
from collections import deque


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def getCount(self):
        return self.count

    def getCells(self):
        return self.cells.copy() # ensure immutability

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if (self.count > 0 and len(self.cells) == self.count):
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if (self.count == 0):
             return self.cells
        return set() 

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if (cell not in self.cells):
            return

        self.cells.remove(cell)
        self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if (cell not in self.cells):
            return
        
        self.cells.remove(cell)

    def is_subset_of(self, sentence):
        if (self.count == 0):
            return False

        if (self == sentence):
            return True
        
        return self.count == sentence.getCount() and self.cells.issubset(sentence.getCells())
    
    def known_safes_from_superset(self, sentence):
        return sentence.getCells().difference(self.cells)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def __create_sentence__(self, cell, count):
        row = cell[0]
        col = cell[1]
        neighbor_cells = set()

        current_count = count

        for i in range(-1, 2): # Loop from -1 to 1
            new_row = row + i

            if new_row < 0 or new_row >= self.height: # invalid row
                continue

            for j in range(-1, 2):
                new_col = col + j
                
                if ((new_row == row and new_col == col) or      # same cell
                    (new_col < 0 or new_col >= self.width)):    # invalid col
                    continue

                neighbour_cell = (new_row, new_col)

                if (neighbour_cell in self.safes):
                    continue

                if (neighbour_cell in self.mines):
                    current_count -= 1
                    continue

                neighbor_cells.add(neighbour_cell)
        
        return Sentence(neighbor_cells, count)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)
        
        sentence = self.__create_sentence__(cell, count)
        self.knowledge.append(sentence)

        self.mark_all_safes()
        self.process_subsets(sentence)

        mines_q = deque()

        for mine in self.find_new_mines():
            mines_q.append(mine)

        while mines_q:
            mine = mines_q.popleft()
            self.mark_mine(mine)

            self.mark_all_safes()
            
            for mine in self.find_new_mines():
                mines_q.append(mine)
                        
    
    def find_new_mines(self):
        found_mines = set()
        for sentence in self.knowledge:
            for mine in sentence.known_mines():
                if mine not in self.mines:
                    found_mines.add(mine)
        return found_mines

    def find_new_safes(self):
        found_safes = set()
        for sentence in self.knowledge:
            for safe in sentence.known_safes():
                if safe not in self.safes:
                    found_safes.add(safe)
        return found_safes
    
    def process_subsets(self, sentence):
        tryOneMoreTime = True

        while (tryOneMoreTime):
            tryOneMoreTime = False
            for superset in self.knowledge:
                if (sentence != superset and sentence.is_subset_of(superset)):
                    tryOneMoreTime = True
                    safes = sentence.known_safes_from_superset(superset)
                    for safe in safes:
                        if (safe in self.safes):
                            continue
                        self.mark_safe(safe)
                        self.mark_all_safes()

    def mark_all_safes(self):
        safe_q = deque()
        visited = set()

        for safe in self.find_new_safes():  
            safe_q.append(safe)
            visited.add(safe)
       
        while safe_q:
            safe = safe_q.popleft()

            self.mark_safe(safe)

            for safe in self.find_new_safes():  
                if safe not in visited:
                    safe_q.append(safe)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for safe in self.safes:
            if safe not in self.moves_made:
                return safe
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        for i in range(self.height):
            for j in range(self.width):
                return (i, j) # pseudo random - easier for testing

        # possible_cells = []
        # for i in range(self.height):
        #     for j in range(self.width):
        #         if ((i, j) not in self.moves_made):
        #             possible_cells.append((i, j))

        # cell_id = random.randint(0, len(possible_cells) - 1)
        # return possible_cells[cell_id]

