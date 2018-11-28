
from pieces import *
from players import *
from board_creator import *
import collections
import copy


class LogicGame:
	def __init__(self, t_color, b_color, radioactive=False, maharajah = False):
		# костыльненько - Maharajah либо False либо (цвет и (позиция))
		if maharajah:
			self.board = BoardCreator.get_maharajah_board(t_color, b_color, *maharajah)
		else:
			self.board = BoardCreator.create_board(t_color, b_color, radioactive)
			# !!!!! для создания тестовых случаев
			# files: 
			# self.board = BoardCreator.create_board_from_file('comp_custel.txt')
			# self.board = BoardCreator.create_board_from_file('check_stalemate.txt')

		self.t_color = t_color
		self.b_color = b_color

		self.over = False
		self.win_color = None
		self.is_in_check_color = None
		self.stalemate = False

		# self.history = [] # (from_pos. to_pos, piece=(color, type))
		self.history = [] # (from_pos, to_pos)
		# self.radioactive_cells = []
		# self.radioactive_cells = collections.deque(maxlen=3)
		self.last_from_poses = collections.deque(maxlen=5) #tuple (from_pos, is_radioactive(True/False))

	def make_move(self, from_pos, to_pos, check_stalemate=True):
		if self.over:
			raise GameOverError

		if not self.is_correct_move(from_pos, to_pos):
			print(from_pos, to_pos, 'is incorrect move')
			# self.print_board()
			raise MoveError

		if self.is_enpassant(from_pos, to_pos):
			self.board[to_pos[0]+from_pos[1]] = ''

		if self.is_custeling(from_pos, to_pos):
			# делается путем наведения короля (from_pos='e1') на ладью (to_pos='a1' or ='h1')
			row = from_pos[1]
			if row != '1' and row != '8':
				raise Exception()
			king_future_place = 'g'+row if to_pos[0]=='h' else 'c'+row
			rook_future_place = 'f'+row if to_pos[0]=='h' else 'd'+row
			color = self.b_color if from_pos[1] == '1' else self.t_color
			self.board[king_future_place] = King(color)
			self.board[rook_future_place] = Rook(color)
			self.board[to_pos] = ''
			self.board[from_pos] = ''
			return

		if isinstance(self.board[to_pos], King) or isinstance(self.board[to_pos], Maharajah): 
			self.over = True
			self.win_color =  self.board[from_pos].color 
			# self.winner = 'Human' if self.board[to_pos].color == 'black' else 'Computer'

		self.board[to_pos] = self.board[from_pos]
		self.board[from_pos] = ''

		if self.need_to_promote_pawn(to_pos):
			self.board[to_pos] = Queen(self.board[to_pos].color)

		act_piece = self.board[to_pos]

		if not act_piece.already_moved:
			act_piece.already_moved = True

		self.history.append((from_pos, to_pos))

		self.last_from_poses.append((from_pos, act_piece.radioactive))
		if check_stalemate:
			next_player_color = 'white' if self.board[to_pos].color == 'black' else 'black'
			self.evaluate_if_no_moves(next_player_color)

	def is_correct_move(self, from_pos, to_pos):
		# проверка на радиоактивность
		for tup in self.last_from_poses:
			if tup[0] == to_pos and tup[1]:
				return False
		if self.is_custeling(from_pos, to_pos):
			# проверка на радиоактивность
			row = to_pos[1]
			rook_next_place = 'f'+row if to_pos[0]=='h' else 'd'+row
			king_next_place = 'g'+row if to_pos[0]=='h' else 'c'+row
			for tup in self.last_from_poses:
				if (tup[0] == rook_next_place and tup[1]) or\
				 (tup[0] == king_next_place and tup[1]):
					return False
			return True
		if self.is_enpassant(from_pos, to_pos):
			return True
		piece = self.board[from_pos]
		if piece == '':
			return False
		if self.board[to_pos] != '' and piece.color == self.board[to_pos].color:
			return False

		can = piece.can_move(from_pos, to_pos) if self.board[to_pos] == '' else piece.can_capture(from_pos, to_pos)
		if not can:
			return False

		return not self.is_barrier_on_pathway(from_pos, to_pos)

	def need_to_promote_pawn(self, to_pos):
		if to_pos[1] != '1' and to_pos[1] != '8':
			return False
		piece = self.board[to_pos]
		if isinstance(piece, Pawn):
			return True
		return False

	def save_session00(self, ses_name):
		def get_history_str000():
			l=[]
			for el in self.history:
				l.append((el[0], el[1], el[2].color, type(el[2]).__name__))
			return l 

		filename = 'saved_sessions/{}.txt'.format(ses_name)
		with open(filename, 'w+') as f:
			for cell in self.board:
				piece = self.board[cell]
				if isinstance(piece, Pawn):
					str_format_piece = '{}("{}", "{}")'.format(type(piece).__name__, piece.color, piece.direction)
				elif isinstance(piece, Knight) and piece.radioactive:
					str_format_piece = '{}("{}", "{}")'.format(type(piece).__name__, piece.color, piece.radioactive)
				else:
					str_format_piece = '{}("{}")'.format(type(piece).__name__, piece.color) if piece else '""'
				f.write("self.board['{}'] = {}\n".format(cell, str_format_piece))

			f.write("self.t_color='{}'\n".format(self.t_color))
			f.write("self.b_color='{}'\n".format(self.b_color))
			f.write("self.history={}\n".format(self.history))
			# print(deque) -> deque([1,2,3], maxlen=2); deque = collections.deque([7, 8, 9], maxlen=2)
			# deque_str = str(self.last_from_poses)[:-1] + ', maxlen={})'.format(self.last_from_poses.maxlen)
			f.write("self.last_from_poses=collections.{}\n".format(self.last_from_poses)) 

	def load_session00(self, ses_name):
		filename = 'saved_sessions/{}.txt'.format(ses_name)
		with open(filename) as f:
			r = f.read()
			lines = r.splitlines()
			# формат line: self.board['a1'] = Pawn(white)
			for line in lines: 
				exec(line)

	def is_enpassant(self, from_pos, to_pos):
		piece = self.board[from_pos]
		if not isinstance(piece, Pawn):
			return False
		if not piece.can_capture(from_pos, to_pos):
			return False
		if piece.color == self.b_color and from_pos[1] != '5' or\
				piece.color == self.t_color and from_pos[1] != '4':
				return False
		enemy_pawn_place = to_pos[0] + from_pos[1]
		if not isinstance(self.board[enemy_pawn_place], Pawn) or self.board[enemy_pawn_place].color == piece.color:
			return False
		# if self.history[-1][1] != enemy_pawn_place:
		# 	return False
		# for moves in self.history:
		# 	if moves[1] == enemy_pawn_place and moves[2] == self.board[enemy_pawn_place]:
		# 		return False
		# return True
		if piece.color == self.t_color:
			this_pawn_init_pos = enemy_pawn_place[0]+'2'
		else:
			this_pawn_init_pos = enemy_pawn_place[0]+'7'
		if self.history[-1][0] == this_pawn_init_pos and self.history[-1][1] == enemy_pawn_place:
			return True
		return False

	def is_custeling(self, from_pos, to_pos):
		if from_pos == 'e1':
			f=7
		if from_pos not in ['e1', 'e8'] or to_pos not in ['a1', 'h1', 'a8', 'h8'] or from_pos[1] != to_pos[1]:
			return False
		if not isinstance(self.board[from_pos], King) or \
				not isinstance(self.board[to_pos], Rook):
			return False
		if self.is_barrier_on_pathway(from_pos, to_pos):
			return False
		if self.board[from_pos].already_moved or self.board[to_pos].already_moved:
			return False
		# print('custelling')
		return True

	def make_custeling0000(self, from_pos, to_pos):
		if to_pos == 'h1':
			king_place = 'g1'
			rook_place = 'f1'
		else:
			king_place = 'c1'
			rook_place = 'd1'

		self.board[king_place] = self.board[from_pos]
		self.board[rook_place] = self.board[to_pos]
		self.board[from_pos] = ''
		self.board[to_pos] = ''

	def is_barrier_on_pathway(self, from_pos, to_pos):
		cells = self.get_pathway_cells(from_pos, to_pos)
		barriers = [self.board[c] for c in cells if not self.board[c] == '']
		return len(barriers) > 0
	def get_pathway_cells(self, from_pos, to_pos):
		""" Возвращает список id клеток, которые находятся на траектории предполагаемого движения
				Если траектория - прямая или диагональ, то возвращает список клеток между from и to
				Иначе пустой список (в случае хода коня или некорректного хода) """

		def get_row(from_pos, to_pos):
			num = from_pos[1]
			min_let = ord(min(from_pos[0], to_pos[0]))
			max_let = ord(max(from_pos[0], to_pos[0]))
			return [chr(x)+num for x in range(min_let+1, max_let)]

		def get_column(from_pos, to_pos):
			letter = from_pos[0]
			min_num = int(min(from_pos[1], to_pos[1]))
			max_num = int(max(from_pos[1], to_pos[1]))
			return [letter+str(x) for x in range(min_num+1, max_num)]

		def get_diagonal(from_pos, to_pos):
			delta = abs(int(from_pos[1]) - int(to_pos[1]))
			min_let = ord(min(from_pos[0], to_pos[0]))
			cells = []
			if (ord(from_pos[0]) - ord(to_pos[0])) * (int(from_pos[1]) - int(to_pos[1])) > 0:
				#   то есть одного знака -- диагональ лев.низ-прав.верх
				min_num = int(min(from_pos[1], to_pos[1]))
				for i in range(1, delta):
					l = min_let + i
					n = min_num + i
					cells.append(chr(l)+str(n))
			else: # диагональ прав.низ - лев.верх
				max_num = int(max(from_pos[1], to_pos[1]))
				for i in range(1, delta):
					l = min_let + i
					n = max_num - i
					cells.append(chr(l) + str(n))
			return cells

		dx = ord(from_pos[0]) - ord(to_pos[0])
		dy = int(from_pos[1]) - int(to_pos[1])
		if abs(dx) == abs(dy):
			return get_diagonal(from_pos, to_pos)
		if dx == 0 and dy != 0:
			return get_column(from_pos, to_pos)
		if dx != 0 and dy == 0:
			return get_row(from_pos, to_pos)
		return []


	def is_in_check(self, king_color):
		king_pos = None # на случай если вызывается, когда короля нет на поле 
		for pos in self.board:
			if self.board[pos] and self.board[pos].color == king_color \
			and (isinstance(self.board[pos], King) or isinstance(self.board[pos], Maharajah)):
				king_pos = pos
				break
		enemy_color = 'white' if (king_color == 'black') else 'black'
		moves = self.get_sorted_movements(enemy_color, avoid_mate=False)
		if not king_pos or not moves:
			return
		if moves[0][1] == king_pos:
			# print(moves[0])
			# print('ISINCHEEK '+king_color)
			return True
		return False

	def get_incheck_king_pos(self, king_color):
		king_pos = None # на случай если вызывается, когда короля нет на поле 
		for pos in self.board:
			if self.board[pos] and self.board[pos].color == king_color \
			and (isinstance(self.board[pos], King) or isinstance(self.board[pos], Maharajah)):
				king_pos = pos
				break
		enemy_color = 'white' if (king_color == 'black') else 'black'
		moves = self.get_sorted_movements(enemy_color, avoid_mate=False)
		if not king_pos or not moves:
			return
		if moves[0][1] == king_pos:
			# print(moves[0])
			# print('ISINCHEEK '+king_color)
			return king_pos


	def get_incheck_king_positions(self):
		king_poses = []
		for pos in self.board:
			if self.board[pos]	and (isinstance(self.board[pos], King) or isinstance(self.board[pos], Maharajah)):
				king_poses.append(pos)

		incheck_k_poses = []
		for k_pos in king_poses:
			enemy_color = 'white' if (self.board[k_pos].color == 'black') else 'black'
			moves = self.get_sorted_movements(enemy_color, avoid_mate=False)
			if moves[0][1] == k_pos:
				incheck_k_poses.append(k_pos)
		return incheck_k_poses

	def evaluate_if_no_moves(self, next_player_color):
		moves = self.get_movements(next_player_color)
		if not moves:
			self.over = True
			self.win_color = 'white' if next_player_color == 'black' else 'black'
			if not self.is_in_check(next_player_color):
				self.stalemate = True



	def evaluate_if_stalemate000(self):
		# не верно, если ходов нет у того, кто сейчас не ходит
		moves_w = self.get_movements('white')
		moves_b = self.get_movements('black')
		if not moves_w or not moves_b:
			self.over = True
			self.stalemate = True
			if not moves_w and not moves_b:
				print('both stalemate')
				self.draw = True
			elif not moves_w:
				print('w stalemate')
				self.win_color = 'black'
			elif not moves_b:
				print('b stalemate')
				self.win_color = 'white'

	# --------------------------
	def get_movements(self, color, avoid_mate=True):
		""" возвращает список ходов (tuple) игрока с цветом color"""
		candidats_to_move = self.get_all_movements(color)  # словарь ходов {from : all where}
		moves = []
		for from_pos in candidats_to_move:
			for to_pos in candidats_to_move[from_pos]:
				if avoid_mate:
					if not self.will_be_mate(from_pos, to_pos):
						moves.append(Move(from_pos, to_pos, self.board))
				else:
					moves.append(Move(from_pos, to_pos, self.board))

		return [(m.from_pos, m.to_pos) for m in moves]

	def get_sorted_movements(self, color, avoid_mate=True):
		""" возвращает список ходов (tuple) игрока с цветом color, упорядоченных по выгоде"""
		candidats_to_move = self.get_all_movements(color)  # словарь ходов {from : all where}
		moves = []
		for from_pos in candidats_to_move:
			for to_pos in candidats_to_move[from_pos]:
				if avoid_mate:
					if not self.will_be_mate(from_pos, to_pos):
						moves.append(Move(from_pos, to_pos, self.board))
				else:
					moves.append(Move(from_pos, to_pos, self.board))
		moves.sort(key=lambda x: x.benefit, reverse=True)
		return [(m.from_pos, m.to_pos) for m in moves]

	def get_all_movements(self, color):
		""" возвращает словарь ходов {from : all where} """
		candidats_to_move = {}
		for cell, piece in self.board.items():
			if piece and piece.color == color:
				movements = self.get_movments_of_piece(cell)
				if len(movements) > 0:
					candidats_to_move[cell] = movements
		return candidats_to_move

	def get_movments_of_piece(self, cell_id): 
		"""возвращает все возможные ходы данной фигуры"""
		piece = self.board[cell_id]
		# empty, enemy = self.get_empty_or_enemy_cells()
		# all_to_pos = empty + enemy
		moves = [to_pos for to_pos in self.board if self.is_correct_move(cell_id, to_pos)]
		return moves

	def get_empty_or_enemy_cells00(self, color):
		""" возвр тапл списков: все пустые и все клетки противника"""
		empty = []
		enemy = []
		for c in self.board.keys():
			piece = self.board[c]
			if not piece:
				empty.append(c)
			elif piece.color != color:
				enemy.append(c)
		return (empty, enemy)

# ----------------

	def get_pseudo_game(self):
		new_game = LogicGame(self.t_color, self.b_color)
		new_game.board = copy.deepcopy(self.board)
		# return new_game
		return copy.deepcopy(self)

	def will_be_mate(self, from_pos, to_pos):
		""" определяет, приведет ли ход игрока к его мату"""
		# return False #!!!!!!!!!!!!!!!!!!!!!!!!
		if not self.is_correct_move(from_pos, to_pos):
			return False
		if isinstance(self.board[to_pos], King) or isinstance(self.board[to_pos], Maharajah):
			return False #если на этом ходе игра и кончится
		game = self.get_pseudo_game()
		game.make_move(from_pos, to_pos, check_stalemate=False)
		if game.is_in_check(self.board[from_pos].color):
			return True
		return False


class Move:
	def __init__(self, from_pos, to_pos, board):
		self.from_pos = from_pos
		self.to_pos = to_pos
		self.board = board
		self.evaluate()

	def evaluate(self):
		piece = self.board[self.to_pos]
		self.benefit = 0 if not piece else piece.weight

		# для en passant
		acting_piece = self.board[self.from_pos]
		if isinstance(acting_piece, Pawn) and acting_piece.can_capture(self.from_pos, self.to_pos) \
				and self.benefit == 0:
			self.benefit = 1

class GameOverError(BaseException):
	pass

class MoveError(BaseException):
	pass