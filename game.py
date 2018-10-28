
from pieces import *
from players import *


class LogicGame:
	def __init__(self):
		self.board = LogicGame.create_board()

		self.over = False
		self.winner = None

		self.history = [] # (from_pos. to_pos, piece)

		# self.last_moved = { 'white':'', 'black':'' } #  2 to_positions


	def create_board():
		def get_strong_piece(x, color):
			if x == 'a' or x == 'h':
				return Rook(color)
			if x == 'b' or x == 'g':
				return Knight(color)
			if x == 'c' or x == 'f':
				return Bishop(color)
			if x == 'd':
				return Queen(color)
			if x == 'e':
				return King(color)
		def get_piece(x, y):
			if y == '2':
				return Pawn('white')
			if y == '7':
				return Pawn('black')
			if y == '1':
				color = 'white'
				return get_strong_piece(x, color)
			if y == '8':
				color = 'black'
				return get_strong_piece(x, color)
			return ''
		board = dict()
		for x in 'abcdefgh':
			for y in '12345678':
				board[x+y] = get_piece(x, y)
		return board


	def make_move(self, from_pos, to_pos, ):
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
			color = 'white' if from_pos[1] == '1' else 'black'
			self.board[king_future_place] = King(color)
			self.board[rook_future_place] = Rook(color)
			self.board[to_pos] = ''
			self.board[from_pos] = ''
			return

		if isinstance(self.board[to_pos], King): 
			self.over = True
			# self.winner = 'Human' if self.board[to_pos].color == 'black' else 'Computer'

		self.board[to_pos] = self.board[from_pos]
		self.board[from_pos] = ''

		if self.need_to_promote_pawn(to_pos):
			self.board[to_pos] = Queen(self.board[to_pos].color)

		act_piece = self.board[to_pos]

		if not act_piece.already_moved:
			act_piece.already_moved = True

		self.history.append((from_pos, to_pos, act_piece))


	def need_to_promote_pawn(self, to_pos):
		if to_pos[1] != '1' and to_pos[1] != '8':
			return False
		piece = self.board[to_pos]
		if isinstance(piece, Pawn):
			return True
		return False


	def save_session(self, ses_name):
		filename = 'saved_sessions/{}.txt'.format(ses_name)

		with open(filename, 'w+') as f:
			for cell in self.board:
				piece = self.board[cell]
				str_format_piece = '{}("{}")'.format(type(piece).__name__, piece.color) if piece else '""'
				f.write("self.board['{}'] = {}\n".format(cell, str_format_piece))


	def load_session(self, ses_name):
		filename = 'saved_sessions/{}.txt'.format(ses_name)
		with open(filename) as f:
			r = f.read()
			lines = r.splitlines()
			# формат line: self.board['a1'] = Pawn(white)
			for line in lines: 
				exec(line)


	def is_correct_move(self, from_pos, to_pos):
		if self.is_custeling(from_pos, to_pos):
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

	def is_enpassant(self, from_pos, to_pos):
		piece = self.board[from_pos]
		if not isinstance(piece, Pawn):
			return False
		if not piece.can_capture(from_pos, to_pos):
			return False
		if piece.color == 'white' and from_pos[1] != '5' or\
				piece.color == 'black' and from_pos[1] != '4':
				return False
		enemy_pawn_place = to_pos[0] + from_pos[1]
		if not isinstance(self.board[enemy_pawn_place], Pawn) or self.board[enemy_pawn_place].color == piece.color:
			return False
		if self.history[-1][1] != enemy_pawn_place:
			return False
		for moves in self.history:
			if moves[1] == enemy_pawn_place and moves[2] == self.board[enemy_pawn_place]:
				return False
		return True



	def make_custeling(self, from_pos, to_pos):
		if from_pos != 'e1' or to_pos not in ['a1', 'h1']:
			raise MoveError
		if not isinstance(self.board[from_pos], King) or \
				not isinstance(self.board[to_pos], Rook):
			raise MoveError
		if self.is_barrier_on_pathway(from_pos, to_pos):
			raise MoveError

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


	def is_custeling(self, from_pos, to_pos):
		if from_pos not in ['e1', 'e8'] or to_pos not in ['a1', 'h1', 'a8', 'h8'] or from_pos[1] != to_pos[1]:
			return False
		if not isinstance(self.board[from_pos], King) or \
				not isinstance(self.board[to_pos], Rook):
			return False
		if self.is_barrier_on_pathway(from_pos, to_pos):
			return False
		if self.board[from_pos].already_moved or self.board[to_pos].already_moved:
			return False
		return True


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



class GameOverError(BaseException):
	pass

class MoveError(BaseException):
	pass


