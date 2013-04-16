'''
Provides the AbstractBoard class, which keeps track of an sgf game
and logical board and returns the moves made whilst moving through the
game tree.

'''

from gomill import sgf, boards

def apply_node_to_board(board, node):
    board = board.copy()
    add_stones = []
    remove_stones = []
    empty_stones = []
    add_playmarker = None

    # First, find and deal with setup stones
    if node.has_setup_stones():
        setup_stones = newnode.get_setup_stones()
        # Add setup stones to board!

    # Now deal with the actual new move, if any

    new_move_colour, new_move_point = node.get_move()
    current_occupied_points = board.list_occupied_points()
    if new_move_point is not None:
        try:
            board.play(new_move_point[0],new_move_point[1],new_move_colour)
        except ValueError:
            print 'SGF played existing point'
        new_occupied_points = board.list_occupied_points()
        if len(new_occupied_points) == len(current_occupied_points) + 1:
            add_stones.append((new_move_point, new_move_colour))
        else:
            for point in new_occupied_points:
                if point not in current_occupied_points:
                    add_stones.append((point[1],point[0]))
            for point in current_occupied_points:
                if point not in new_occupied_points:
                    remove_stones.append((point[1],point[0]))
        add_playmarker = new_move_point


    instructions = {}
    if len(add_stones) > 0:
        instructions['add'] = add_stones
    if len(remove_stones) > 0:
        instructions['remove'] = remove_stones
    if len(empty_stones) > 0:
        instructions['empty'] = empty_stones
    if add_playmarker is not None:
        instructions['playmarker'] = add_playmarker

    return (board, instructions)


def compare_boards(old, new):
    add_stones = []
    remove_stones = []

    old_stones = old.list_occupied_points()
    new_stones = new.list_occupied_points()
    for point in new_stones:
        if point not in old_stones:
            add_stones.append((point[1],point[0]))
    for point in old_stones:
        if point not in new_stones:
            remove_stones.append((point[1],point[0]))

    instructions = {}
    if len(add_stones) > 0:
        instructions['add'] = add_stones
    if len(remove_stones) > 0:
        instructions['remove'] = remove_stones

    return instructions

    

class AbstractBoard(object):
    def __init__(self,game=None):
        if game is None:
            game = sgf.Sgf_game(19)

        self.game = game
        self.prisoners = [0,0]
        self.variation_index = 0

        self.boards = {}
        self.curnode = game.get_root()
        self.boards[self.curnode] = boards.Board(self.game.size)

    def load_sgf_from_file(self,filen):
        fileh = open(filen,'r')
        sgfdata = fileh.read()
        fileh.close()
        self.game = sgf.Sgf_game.from_string(sgfdata)
        self.reset_position()

    def load_sgf_from_text(self, sgftext):
        self.game = sgf.Sgf_game.from_string(sgftext)
        self.reset_posiiton()

    def set_sgf(self,sgf):
        self.game = sgf
        self.reset_position()

    def reset_position(self):
        self.curnode = self.game.get_root()
        self.boards = {}
        self.boards[self.curnode] = boards.Board(self.game.size)

    def advance_position(self,*args,**kwargs):
        curnode = self.curnode
        curboard = self.boards[curnode]
        if len(curnode) > 0:
            newnode = self.curnode[0]
        else:
            return {}

        self.curnode = newnode
        newboard = curboard.copy()

        
        newboard, instructions = apply_node_to_board(newboard, newnode)

        self.boards[newnode] = newboard

        return instructions


    def retreat_position(self,*args,**kwargs):
        curnode = self.curnode
        curboard = self.boards[curnode]
        if curnode.parent is not None:
            newnode = self.curnode.parent
        else:
            return {}

        self.curnode = newnode
        if self.boards.has_key(newnode):
            newboard = self.boards[newnode]
        else:
            print 'Reconstruct board'

        self.boards[newnode] = newboard

        instructions = compare_boards(curboard, newboard)

        newmove = newnode.get_move()
        if newmove[1] is not None:
            instructions['playmarker'] = newmove[1]

        return instructions

    def jump_to_node(self,node):
        oldboard = self.boards[self.curnode]
        self.curnode = node
        newboard = self.get_or_build_board(node)
        return compare_boards(oldboard,newboard)

    def get_or_build_board(self, node):
        if not self.boards.has_key(node):
            self.build_boards_to_node(node)
        return self.boards[node]

    def build_boards_to_node(self, node, replace=False):
        precursor_nodes = self.game.get_sequence_above(node)
        board = boards.Board(self.game.size)
        board, instructions = apply_node_to_board(board,precursor_nodes[0])
        self.boards[precursor_nodes[0]] = board

        for i in range(1,len(precursor_nodes)):
            curnode = precursor_nodes[i]
            if (not self.boards.has_key(curnode)) or replace:
                board, instructions = apply_node_to_board(board, curnode)
                self.boards[curnode] = board
            else:
                board = self.boards[curnode]

        curnode = node
        board, instructions = apply_node_to_board(board, node)
        self.boards[node] = board

    def stones_at_node(self,node):
        return map(lambda j: j.get_move(),self.game.get_sequence_above(node))
