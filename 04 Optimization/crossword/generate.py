import sys
from collections import deque

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.crossword.variables:
            for word in self.crossword.words:
                if variable.length != len(word):
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
 
        # crossword.overlaps[v1, v2]
        # The pair (i, j) should be interpreted to mean that the i-th character of v1’s value must be the same as the j-th character of v2’s value.
        overlap = self.crossword.overlaps[x, y]

        if (overlap == None):
            return False
        
        i,j = overlap

        visited = set()
        for wordX in self.domains[x]:
            for wordY in self.domains[y]:
                if wordX[i] == wordY[j]:
                    visited.add(wordX)
                    break

        if len(visited) == len(self.domains[x]):
            return False
        
        self.domains[x] = visited
        return True

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        queueArcs = set()

        if arcs != None:
            queueArcs = arcs
        else:
            for variables in self.crossword.overlaps.keys():
                x, y = variables
                if (x, y) not in queueArcs and (y, x) not in queueArcs:
                    queueArcs.add((x, y))

        queue = deque(queueArcs)

        while queue:
            variables = queue.popleft()  # Remove and get the first element
            variableX, varuableY = variables

            if self.revise(variableX, varuableY):
                if len(self.domains[variableX]) == 0:
                    return False
                for neighbour in self.crossword.neighbors(variableX):
                    if neighbour != varuableY:
                        queue.append((neighbour, variableX))
        
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return len(self.crossword.variables) == len(assignment.values())

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        uniqueWords = set()
        for variable in assignment.keys():
            word = assignment[variable]

            if word in uniqueWords:
                return False
            
            uniqueWords.add(word)

            if len(word) != variable.length:
                return False
            
            for neighbour in self.crossword.neighbors(variable):
                overlap = self.crossword.overlaps[variable, neighbour]

                if overlap == None or neighbour not in assignment:
                    continue
                
                i, j = overlap
                if word[i] != assignment[neighbour][j]:
                    return False
            
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        valueCount = dict()

        for word in self.domains[var]:
            valueCount[word] = 0
            for neighbor in self.crossword.neighbors(var) - assignment.keys():
                if word in self.domains[neighbor]:
                    valueCount[word] += 1

        return sorted(valueCount, key=valueCount.get)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        result = None
        
        for variable in self.crossword.variables: 
            if variable in assignment:
                continue
            if (result is None or
                len(self.domains[variable]) < len(self.domains[result]) or
                (len(self.domains[variable]) == len(self.domains[result]) and 
                len(self.crossword.neighbors(variable)) > len(self.crossword.neighbors(result)))):
                result = variable
       
        return result

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        variable = self.select_unassigned_variable(assignment)

        for value in self.domains[variable]:
            assignment[variable] = value

            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result

            assignment.pop(variable)

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
