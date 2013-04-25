'''
Provides the AbstractBoard class, which keeps track of an sgf game
and logical board and returns the moves made whilst moving through the
game tree.

'''

from gomill import sgf, boards

# class ScoreBoard:
#     def __init__(self,size=19):
#         self.scoringboard = boards.Board(size)
#         self.board = [[] for i in range(size)]
#         self.size = size
#     def set_board(self,arr):
#         self.board.board = arr
#     def get_score(self):
#         self.scoringboard.board = self.remove_dead()
#         return self.board.area_score()
#     def toggle_status_at(self,coord):
#         cur = self.board[coord[0]][coord[1]]
#         if cur == 'w':
#             self.board[coord[0]][coord[1]] = 'dw'
#         elif cur == 'b':
#             self.board[coord[0]][coord[1]] = 'db'
#         return self.get_score()
#     def propagate_dead(self):
#         board = self.board
#         changing = True
#         while changing:
#             for x in range(self.size):
#                 for y in range(self.size):
#                     cur = board[x][y]
                    
            
        


def get_sgf_from_file(filen):
    fileh = open(filen)
    string = fileh.read()
    game = sgf.Sgf_game.from_string(string)
    return game

def argsconverter_get_gameinfo_from_file(row_index,filen):
    info = get_gameinfo_from_file(filen)
    info['size_hint'] = (1.,None)
    info['height'] = (70,'sp')
    return info

def get_gameinfo_from_file(filen):
    try:
        info = get_gameinfo_from_sgf(get_sgf_from_file(filen))
    except:
        print 'Something went wrong with',filen
        info = {'wname':'[color=ff0000]ERROR[/color] reading file'}
    info['filepath'] = filen
    return info

def get_gameinfo_from_sgf(game):
    info = {}
    bname = game.get_player_name('b')
    if bname is not None:
        info['bname'] = bname
    wname = game.get_player_name('w')
    if wname is not None:
        info['wname'] = wname
    komi = game.get_komi()
    if komi is not None:
        info['komi'] = game.get_komi()
    size = game.get_size()
    if size is not None:
        info['gridsize'] = game.get_size()
    handicap = game.get_handicap()
    if handicap is not None:
        info['handicap'] = game.get_handicap()
    rootnode = game.get_root()
    props = rootnode.properties()
    if 'RE' in props:
        info['result'] = rootnode.find_property('RE')
    if 'SO' in props:
        info['source'] = rootnode.find_property('SO')
    if 'BR' in props:
        info['brank'] = rootnode.find_property('BR')
    if 'WR' in props:
        info['wrank'] = rootnode.find_property('WR')
    if 'BT' in props:
        info['bteam'] = rootnode.find_property('BT')
    if 'WT' in props:
        info['wteam'] = rootnode.find_property('WT')
    if 'CP' in props:
        info['copyright'] = rootnode.find_property('CP')
    if 'DT' in props:
        info['date'] = rootnode.find_property('DT')
    if 'EV' in props:
        info['event'] = rootnode.find_property('EV')
    if 'GN' in props:
        info['gname'] = rootnode.find_property('GN')
    if 'GC' in props:
        info['gamecomment'] = rootnode.find_property('GC')
    if 'OT' in props:
        info['overtime'] = rootnode.find_property('OT')
    if 'RU' in props:
        info['rules'] = rootnode.find_property('RU')
    if 'TM' in props:
        try:
            info['timelim'] = rootnode.find_property('TM')
        except:
            pass
    if 'US' in props:
        info['user'] = rootnode.find_property('US')
    return info
    
    


def get_markers_from_node(node):
    properties = node.properties()
    instructions = {'marker':[]}
    markers = []
    if 'TR' in properties:
        node_markers = node.find_property('TR')
        for marker in node_markers:
            markers.append((marker,'TR'))
    if 'SQ' in properties:
        node_markers = node.find_property('SQ')
        for marker in node_markers:
            markers.append((marker,'SQ'))
    if 'CR' in properties:
        node_markers = node.find_property('CR')
        for marker in node_markers:
            markers.append((marker,'CR'))
    if 'MA' in properties:
        node_markers = node.find_property('MA')
        for marker in node_markers:
            markers.append((marker,'MA'))
    if 'LB' in properties:
        node_markers = node.find_property('LB')
        for marker in node_markers:
            markers.append((marker[0],'LB',marker[1]))
        

    if len(markers) > 0:
        return {'markers': markers}
    else:
        return {}

def get_setupstones_from_node(node):
    print 'Getting setupstones!'
    black, white, empty = node.get_setup_stones()
    stones = []
    for stone in black:
        stones.append((stone,'b'))
    for stone in white:
        stones.append((stone,'w'))
    for stone in empty:
        stones.append((stone,'e'))
    print 'setup stones returned:', stones
    return stones
        
def check_variations_in_node(node):
    if node.parent is None:
        return (1,1)
    else:
        return (node.parent.index(node) + 1,len(node.parent))

def get_variations_from_node(node):
    vars = []
    if node.parent is not None:
        parent = node.parent
        if len(parent) > 1:
            for child in parent:
                if child is not node:
                    childmove = child.get_move()
                    if childmove[0] is not None and childmove[1] is not None:
                        vars.append((childmove[0],childmove[1],parent.index(child)+1))
    return vars

def apply_node_to_board(board, node):
    board = board.copy()
    add_stones = []
    remove_stones = []
    empty_stones = []
    add_playmarker = None

    current_occupied_points = board.list_occupied_points()

    # First, find and deal with setup stones
    if node.has_setup_stones():
        print '### Node has setup stones!'
        setup_stones = get_setupstones_from_node(node)
        if len(setup_stones) > 0:
            for stone in setup_stones:
                coords,col = stone
                if col in ['b','w']:
                    board.board[coords[0]][coords[1]] = col
                elif col == 'e':
                    board.board[coords[0]][coords[1]] = None
            

    # Now deal with the actual new move, if any

    new_move_colour, new_move_point = node.get_move()
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


    instructions = {}
    if len(add_stones) > 0:
        instructions['add'] = add_stones
    if len(remove_stones) > 0:
        instructions['remove'] = remove_stones
    if len(empty_stones) > 0:
        instructions['empty'] = empty_stones

    nonstone_instructions = get_nonstone_from_node(node)
    instructions.update(nonstone_instructions)

    #instructions.update(setup_stones)

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

def get_nonstone_from_node(node):
    instructions = {}
    
    node_markers = get_markers_from_node(node)
    instructions.update(node_markers)

    variations = check_variations_in_node(node)
    if variations > 1:
        instructions['variations'] = variations

    new_move_colour, new_move_point = node.get_move()
    if new_move_point is not None:
        add_playmarker = new_move_point
        instructions['playmarker'] = add_playmarker

    comment = get_comment_from_node(node)
    if len(comment) > 0:
        instructions['comment'] = comment

    nextplayer = get_nextplayer_from_node(node)
    instructions['nextplayer'] = nextplayer

    varposs = get_variations_from_node(node)
    if len(varposs) > 0:
        instructions['varpositions'] = varposs

    return instructions

def get_nextplayer_from_node(node):
    if 'PL' in node.properties():
        return node.find_property('PL')
    else:
        props = node.properties()
        if 'W' in props:
            return 'b'
        if 'B' in props:
            return 'w'
        if 'HA' in props:
            return 'w'
        if node.parent is None:
            return 'b'
    return 'a'

def get_comment_from_node(node):
    props = node.properties()
    annotations = []
    judgements = []
    comment = ''
    if 'N' in props:
        annotations.append('Node name: [b]%s[/b]' % node.find_property('N'))
    if 'DM' in props:
        judgements.append('[b]even position[/b]')
    if 'GB' in props:
        judgements.append('[b]good for black[/b]')
    if 'GW' in props:
        judgements.append('[b]good for white[/b]')
    if 'HO' in props:
        judgements.append('[b]hotspot[/b]')
    if 'UC' in props:
        judgements.append('[b]unclear position[/b]')
    if 'BM' in props:
        judgements.append('[b]bad move[/b]')
    if 'DO' in props:
        judgements.append('[b]doubtful move[/b]')
    if 'IT' in props:
        judgements.append('[b]interesting move[/b]')
    if 'TE' in props:
        judgements.append('[b]tesuji[/b]')
    if 'V' in props:
        annotations.append('Value: %d' % node.find_property('V'))
    if 'C' in props:
        comment = node.find_property('C')
    text = ''
    if len(annotations) > 0:
        text = '\n'.join(annotations)
    if len(judgements) > 0:
        text = ''.join((text,'SGF annotations: ',', '.join(judgements)))
    if len(comment) > 0:
        if len(text) > 0:
            text = ''.join((text,'\n----------\n',comment))
        else:
            text = comment

    return text
    
    
    
    

class AbstractBoard(object):
    def __init__(self,game=None):
        if game is None:
            game = sgf.Sgf_game(19)

        self.game = game
        self.prisoners = [0,0]
        self.variation_index = 0

        self.boards = {}
        self.curnode = game.get_root()
        board = boards.Board(self.game.size)
        board, instructions = apply_node_to_board(board,self.curnode)
        self.boards[self.curnode] = board
        self.varcache = {}

    def load_sgf_from_file(self,filen):
        print 'asked to load from',filen
        fileh = open(filen,'r')
        sgfdata = fileh.read()
        fileh.close()
        try:
            self.game = sgf.Sgf_game.from_string(sgfdata)
        except ValueError:
            self.game = sgf.Sgf_game(19)
        self.reset_position()


    def load_sgf_from_text(self, sgftext):
        self.game = sgf.Sgf_game.from_string(sgftext)
        self.reset_position()

    def set_sgf(self,sgf):
        self.game = sgf
        self.reset_position()

    def reset_position(self):
        self.curnode = self.game.get_root()
        self.boards = {}
        self.varcache = {}
        board = boards.Board(self.game.size)
        board, instructions = apply_node_to_board(board,self.curnode)
        self.boards[self.curnode] = board
        return instructions

    def jump_to_varbranch(self):
        curnode = self.curnode
        while len(curnode) <= 1 and curnode.parent is not None:
            print 'curnode',len(curnode)
            curnode = curnode.parent
        if self.varcache.has_key(curnode):
            self.varcache[curnode] = 0
        return self.jump_to_node(curnode)
            

    def advance_position(self,*args,**kwargs):
        curnode = self.curnode
        curboard = self.boards[curnode]
        if len(curnode) > 0:
            if self.varcache.has_key(curnode):
                newnode = self.curnode[self.varcache[curnode]]
            else:
                newnode = self.curnode[0]

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

        nonstone_instructions = get_nonstone_from_node(newnode)
        instructions.update(nonstone_instructions)

        return instructions

    def increment_variation(self):
        if self.curnode.parent is not None:
            parentnode = self.curnode.parent
            newind = (parentnode.index(self.curnode)+1) % len(parentnode)
            newnode = parentnode[newind]
            self.varcache[parentnode] = newind
            return self.jump_to_node(newnode)
        else:
            return {}

    def decrement_variation(self):
        if self.curnode.parent is not None:
            parentnode = self.curnode.parent
            newind = (parentnode.index(self.curnode)-1) % len(parentnode)
            newnode = parentnode[newind]
            self.varcache[parentnode] = newind
            return self.jump_to_node(newnode)
        else:
            return {}
            
            

    def jump_to_node(self,node):
        oldboard = self.boards[self.curnode]
        self.curnode = node
        newboard = self.get_or_build_board(node)
        instructions = compare_boards(oldboard,newboard)
        nonstone_instructions = get_nonstone_from_node(node)
        instructions.update(nonstone_instructions)
        self.build_varcache_to_node(node)
        return instructions

    def add_new_node(self,coord,colour,newmainline=False,jump=True):
        curboard = self.boards[self.curnode]
        if curboard.board[coord[0]][coord[1]] is not None:
            print 'Addition denied, stone already exists!'
            return {}
        curnode = self.curnode
        for entry in self.curnode:
            ecolour,ecoord = entry.get_move()
            if ecolour == colour and ecoord[0] == coord[0] and ecoord[1] == coord[1]:
                return self.jump_to_node(entry)
        if not newmainline:
            newnode = self.curnode.new_child()
        else: 
            newnode = self.curnode.new_child(0)
        newnode.set_move(colour,coord)
        if jump:
            return self.jump_to_node(newnode)
        else:
            return {}

    def replace_next_node(self,coord,colour):
        if self.varcache.has_key(self.curnode):
            newnode = self.curnode[self.varcache[curnode]]
        else:
            newnode = self.curnode[0]
        newnode.set_move(colour,coord)
        self.recursively_destroy_boards_from(newnode)
        return self.jump_to_node(newnode)

    def insert_before_next_node(self,coord,colour):
        if self.varcache.has_key(self.curnode):
            reparentnode = self.curnode[self.varcache[curnode]]
        else:
            reparentnode = self.curnode[0]

        self.add_new_node(coord,colour,jump=False)
        reparentnode.reparent(self.curnode[-1])
        self.recursively_destroy_boards_from(reparentnode)
        return self.jump_to_node(self.curnode[-1])

    def recursively_destroy_boards_from(self,node):
        if self.boards.has_key(node):
            deadboard = self.boards.pop(node)
        for child in node:
            self.recursively_destroy_boards_from(child)

    def build_varcache_to_node(self,node):
        while node.parent is not None:
            newnode = node.parent
            if len(newnode) > 1:
                nodeind = newnode.index(node)
                self.varcache[newnode] = nodeind
            node = newnode


    def get_next_coords(self):
        curnode = self.curnode
        if len(curnode) < 1:
            return (None,None)
        if self.varcache.has_key(curnode):
            newnode = curnode[varcache[curnode]]
        else:
            newnode = curnode[0]
        return newnode.get_move()[1]

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

    def get_player_names(self):
        wname = self.game.get_player_name('w')
        bname = self.game.get_player_name('b')
        if wname is not None:
            wname = ''.join(wname.splitlines())
        else:
            wname = 'Unknown'
        if bname is not None:
            bname = ''.join(bname.splitlines())
        else:
            bname = 'Unknown'
        return (wname,bname)

    def get_player_ranks(self):
        try:
            wrank = self.game.root.find_property('WR')
        except KeyError:
            wrank = None
        try:
            brank = self.game.root.find_property('BR')
        except KeyError:
            brank = None
        if wrank is not None:
            wrank = '(' + ''.join(wrank.splitlines()) + ')'
        else:
            wrank = ''
        if brank is not None:
            brank = '(' + ''.join(brank.splitlines()) + ')'
        else:
            brank = ''
        return (wrank,brank)

    def do_children_exist(self):
        if len(self.curnode) > 0:
            return True
        else:
            return False
    
        
