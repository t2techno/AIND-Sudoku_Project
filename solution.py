# visualization
assignments = []

# Prep

# Cross_Product Function
def cross(A, B):
    # Cross product of elements in A and elements in B.
    return [a+b for a in A for b in B]

rows = 'ABCDEFGHI'
cols = '123456789'

# All-boxs in the game
boxes = cross(rows,cols)

# Column, Row, and Square units
col_units    = [cross(r,cols) for r in rows]
row_units    = [cross(rows,c) for c in cols]
square_units = [cross(a,b) for a in ['ABC','DEF','GHI'] for b in ['123','456','789']]

# Left->Right diagonal
left_diag_units   = [rows[i]+cols[i] for i in range(0,9)]
# Right->Left diagonal
right_diag_units  = [rows[i]+cols[8-i] for i in range(0,9)]

# All possible units, including the diagonal units
# Including the diagonals here is all that was needed to  implement diagonal Sudoku
units_list = col_units + row_units + square_units + [left_diag_units] + [right_diag_units]

# A dictionary with a box address as key, and the list of units for the box as value
# Will be 3 lists for all boxes except those in the diagonals
# E5 is the only one with 5 units, as it is in both diagonals
units = {box: [unit for unit in units_list if box in unit] for box in boxes}

# A dictionary with box address as key, and a set of peers from all units as value
peers = {box: set(sum(units[box],[]))-set([box]) for box in boxes}

# visualization
def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    # walking through each unit
    for unit in units_list:
        # keep any box with exactly two possible values
        len_two = [box for box in unit if len(values[box]) == 2]

        double_check = [] # holds values to find doubles
        naked_twin = []   # holds 'naked_twin values'

        # Walk through len_two, if a value is not in double_check, append, else its a naked twin
        for box in len_two:
            if values[box] not in double_check:
                double_check.append(values[box])
            else:
                naked_twin.append(values[box])

        # If there were naked_twins found
        # walk through each twin and compare with boxes in the unit
        if len(naked_twin) > 0:
            for twin_value in naked_twin:
                for box in unit:
                # if they're not equal, the box is not a twin
                    if values[box] != twin_value:
                    # remove necessary values
                        for num in twin_value:
                            values = assign_value(values, box, values[box].replace(num,''))
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    # Creates specified dictionary, use zip in loop as the values are 1-1 between box and grid
    values = {box: '123456789' if value == '.' else value for box,value in zip(boxes,grid)}
    return values

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    # From class
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def eliminate(values):
    # Find boxes with solved values
    solved_boxes = [box for box in boxes if len(values[box]) == 1]
    for box in solved_boxes:
        value = values[box]
        # Walk through peers of solved box, and remove solved value if it is a possibility
        for peer in peers[box]:
            values = assign_value(values,peer,values[peer].replace(value,''))

    return values


def only_choice(values):
    for unit in units_list:
        for num in '123456789':
            # Walk through every box in a unit, and get count of each num,1-9
            digit_count = [box for box in unit if num in values[box]]
            # If the number only appears once as an option in the unit
            # Then it has to belong to that box
            if len(digit_count) == 1:
                values = assign_value(values,digit_count[0],num)

    return values

# Combines reduction techniques into one function, includes a check for an impossible board
def reduce_puzzle(values):
    stalled = False
    
    # While the board changes between reductions
    while not stalled:
        # Get number of solved boxes before running reduction
        solved_boxes_before = len([box for box in boxes if len(values[box]) == 1])

        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)

        # Get number of solved boxes after running reduction
        solved_boxes_after = len([box for box in boxes if len(values[box]) == 1])

        # If they are the same, nothing was accomplished, end loop
        if solved_boxes_before == solved_boxes_after:
            stalled = True

        # If a box has 0 possible values, it's a bad board, need to end this branch of search tree
        if any(len(values[box]) == 0 for box in boxes):
            return False

    return values

# Recursive function to solve a board
def search(values):
    #Run reduction techniques
    values = reduce_puzzle(values)
    
    # If false was returned, Bad Solution
    if values == False:
        return False
    
    #All possibilities are length 1, Solved, end puzzle and return board
    if all(len(values[box]) == 1 for box in boxes):
        return values

    # Get the box with smallest num of possibilities
    nums,s = min((len(values[box]),box) for box in boxes if len(values[box]) > 1)

    for num in nums:
        # Create new board with same values
        values_copy = values.copy()
        
        # Assign possibility to new board
        values_copy = assign_value(values_copy,s,num)
        
        # Try to solve board with chosen possibility
        attempt = search(values_copy)
        
        # If it is not false, board is solved and can be returned
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    # Create dictionary out of string grid like our alg. expects
    values = grid_values(grid)
    
    # Find solution
    solution = search(values)
    return solution

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
