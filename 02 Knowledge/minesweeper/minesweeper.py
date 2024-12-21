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

    def get_count(self):
        return self.count

    def get_cells(self):
        return self.cells.copy() # ensure immutability

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count
    
    # for checking if element is in set
    def __hash__(self):
        # Hash based on frozenset of cells and count
        return hash((frozenset(self.cells), self.count))

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

    def can_make_new_knowledge_with(self, sentence):
        """
        Check if is it possible to create a new sentence by
        merging knowledge from 2 sentences
        E.g. {A, B, C} = 1 and {A, B, C, D, E} = 2
        results in {D, E} = 1
        """
        if (self.count == 0 or sentence.get_count() == 0):
            return False
        
        if (self.count == sentence.get_count()):
            return False

        if (self == sentence):
            return False
        
        return self.cells.issubset(sentence.get_cells()) or sentence.get_cells().issubset(self.cells)
    
    def get_new_knowledge(self, sentence):
        """
        Create a new sentence by merging knowledge from 2 sentences
        E.g. {A, B, C} = 1 and {A, B, C, D, E} = 2
        results in {D, E} = 1
        """
        if (sentence.get_count() >  self.count):
            new_count = sentence.get_count() - self.count
            new_cells = sentence.get_cells().difference(self.cells)
            return Sentence(new_cells, new_count)
        else:
            new_count = self.count - sentence.get_count()
            new_cells = self.cells.difference(sentence.get_cells())
            return Sentence(new_cells, new_count)


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

    def create_sentence(self, cell, count):
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
        
        return Sentence(neighbor_cells, current_count)

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
        
        sentence = self.create_sentence(cell, count)
        self.knowledge.append(sentence)

        # mark safes found from new sentence
        for safe in sentence.known_safes().copy():
            self.mark_safe(safe)

        mines_q = deque()

        # to mark mines found from new sentence
        for mine in self.find_new_mines():
            mines_q.append(mine)

        while mines_q:
            mine = mines_q.popleft()

            if mine in self.mines:
                continue

            self.mark_mine(mine)

            # mine found may lead to new safes found
            # mark found safes
            for safe in self.find_new_safes():
                self.mark_safe(safe)
            
            # mark safes may lead to new mines found
            # add them to queue to process them later
            for mine in self.find_new_mines():
                mines_q.append(mine)

        self.find_new_knowledges(sentence)
        self.print_knowledge()
                        
    
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
    
    def find_new_knowledges(self, base_sentence):
        base_sentence_q = deque()
        visited = set()
        base_sentence_q.append(base_sentence)

        while (base_sentence_q):
            base = base_sentence_q.popleft()

            for sentence in self.knowledge:
                if (base.can_make_new_knowledge_with(sentence)):
                    new_knowledge = base.get_new_knowledge(sentence)
                    if (new_knowledge not in visited):
                        visited.add(new_knowledge)
                        base_sentence_q.append(new_knowledge)
                        self.knowledge.append(new_knowledge)

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
            
        # There can be a situation when safe cell is isolated by mines.
        # But it may be a mine too, can't check, cell is isolated.
        # Let's try, no other option left, otherwise random 
        # which is not better than this guess. 
        for i in range(self.height):
            for j in range(self.width):
                cell = (i, j)
                if (cell not in self.moves_made and cell not in self.mines):
                    return cell

        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # for i in range(self.height):
        #     for j in range(self.width):
        #         if ((i, j) not in self.moves_made):
        #             return (i, j) # pseudo random - easier for testing

        possible_cells = []
        for i in range(self.height):
            for j in range(self.width):
                if ((i, j) not in self.moves_made):
                    possible_cells.append((i, j))

        cell_id = random.randint(0, len(possible_cells) - 1)
        return possible_cells[cell_id]

    def print_knowledge(self):
        for i in range(self.height):
            print()
            for j in range(self.width):
                if ((i, j) in self.moves_made):
                    print('.', end=" ")
                elif ((i, j) in self.safes):
                    print('+', end=" ")
                elif ((i,j) in self.mines):
                    print('X', end=" ")
                else:
                    print(' ', end=" ")
        print()
