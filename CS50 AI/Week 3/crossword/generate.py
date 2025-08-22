import sys
import random

from crossword import *


class CrosswordCreator:

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword: Crossword = crossword
        self.domains = {
            var: self.crossword.words.copy() for var in self.crossword.variables
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
            (self.crossword.width * cell_size, self.crossword.height * cell_size),
            "black",
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border, i * cell_size + cell_border),
                    (
                        (j + 1) * cell_size - cell_border,
                        (i + 1) * cell_size - cell_border,
                    ),
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (
                                rect[0][0] + ((interior_size - w) / 2),
                                rect[0][1] + ((interior_size - h) / 2) - 10,
                            ),
                            letters[i][j],
                            fill="black",
                            font=font,
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
        for variable, domain in self.domains.items():
            for word in list(domain):
                if (
                    len(word) != variable.length
                ):  # Only store those words which are of equal length to the corsswords
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revise = False
        intersections = self.crossword.overlaps[
            (x, y)
        ]  # Get all the overlaps, since those are the binary constraints
        for X in list(self.domains[x]):
            found = False
            for Y in list(self.domains[y]):
                if (
                    X[intersections[0]] == Y[intersections[1]]
                ):  # If there is atleast one word in both the domains, which has a letter at both positions then continue
                    found = True
                    break
            if found == False:
                self.domains[x].remove(X)
                revise = True

        return revise

    def ac3(self, arcs: list = None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = [
                k for k, v in self.crossword.overlaps.items() if v != None
            ]  # Getting the keys i.e variable pairs with binary constraints
        while len(arcs) != 0:
            pair = arcs.pop(0)
            if self.revise(*pair):
                if len(self.domains[pair[0]]) == 0:
                    return False
                for Z in list(self.crossword.neighbors(pair[0])):
                    if Z == pair[1]:
                        continue
                    arcs.append((Z, pair[0]))  # The order here is important
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Check if var equals no of assignments
        return len(assignment.keys()) == len(self.domains.keys())

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for (
            variable,
            assigned_word,
        ) in assignment.items():  # Iterating through Assignments
            if assigned_word == "":  # If Empty Continue
                continue
            elif variable.length != len(assigned_word):  # Violates Unary Constraint
                return False
            else:
                for neighbour in self.crossword.neighbors(
                    variable
                ):  # Checking all its neighbours
                    if (
                        neighbour not in assignment.keys()
                        or assignment[neighbour] == ""
                    ):
                        continue
                    elif neighbour.length != len(assignment[neighbour]):
                        return False
                    else:  # Since both variables are neighbours so no need to check for constraint existance
                        intersection_point = self.crossword.overlaps[
                            (variable, neighbour)
                        ]  # Getting the common point
                        if (
                            assignment[neighbour][intersection_point[1]]
                            != assigned_word[intersection_point[0]]
                        ):  # Checking if they both have same char at that point
                            return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        neighbours = self.crossword.neighbors(var)

        for n in list(neighbours):
            if n in assignment.keys():
                neighbours.remove(n)

        # A dict to keep trach of the number of counts a word will gain the more favourable it is for its neighbours
        # Decremenet if its disadvantageous

        counter_dict = {var: 0 for var in self.domains[var]}

        for words in self.domains[var]:
            for n in neighbours:
                pair = self.crossword.overlaps[(var, n)]  # Intersection Point
                for neighbours_words in self.domains[n]:
                    if words[pair[0]] == neighbours_words[pair[1]]:
                        counter_dict[words] += 1
                    else:
                        counter_dict[words] -= 1

        sorted_counter_dict = dict(
            sorted(counter_dict.items(), key=lambda item: item[1], reverse=True)
        )
        return list(sorted_counter_dict.keys())

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Select Unssigned Vars
        unassigned_vars = {
            var: len(self.domains[var])
            for var in self.domains.keys()
            if var not in assignment.keys()
        }

        sorted_dict_by_domain_size = dict(
            sorted(unassigned_vars.items(), key=lambda item: item[1])
        )
        new_var_list = []
        min_value = list(sorted_dict_by_domain_size.values())[0]

        # Get first n equal min variables
        for var, domain_size in sorted_dict_by_domain_size.items():
            if min_value == domain_size:
                new_var_list.append(var)
            else:
                break

        # If equal to 1 then return the variable
        if len(new_var_list) == 1:
            return new_var_list[0]

        # Else we move towards the degree size

        degree_dict = {var: len(self.crossword.neighbors(var)) for var in new_var_list}
        sorted_dict_by_degree = dict(
            sorted(degree_dict.items(), key=lambda item: item[1])
        )
        new_var_list = []
        min_value = list(sorted_dict_by_degree.values())[0]
        for var, domain_size in sorted_dict_by_degree.items():
            if min_value == domain_size:
                new_var_list.append(var)

        # Returning Randomly
        return random.choice(new_var_list)

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # If assignment Complete, halt
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        self.order_domain_values(var, assignment)
        for word in self.domains[var]:
            new_assignment = assignment.copy()
            new_assignment[var] = word
            if self.consistent(new_assignment):
                self.ac3()
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result

        # No possible assignment, fall back
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
