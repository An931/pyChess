
from pieces import *
# from board import *
from players import *

# игра - то, что запускается один раз при запске приложения

# изменить:
# 0 полностью прописать сохр и восст-е сессии ++ вроде есть ++
	# (+ метод определения захваченных фигур)
	# + изменить представление фигур в строк
# 1 сделать инициализацию поля только из файла
# 2 связать гуи
# 3 прописать сохрание и чтение сессии
# 4 убрать (переделать) extract_hum_move
# 5 можно убрать класс доски, сделав ее простым словарем
# игрок всегда играет белыми
# убрать историю (добавлю потом если понадрбится)

class Game:
	def __init__(self):
		self.board = self.create_board()
		self.comp = Computer(self)
		self.over = False
		self.winner = None

		# self.last_moved = { 'white':None, 'black':None } # for check en passant
		self.last_moved = { 'white':'', 'black':'' } #  2 to_positions


	def create_board(self):
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

	def make_human_move_0(self, from_pos, to_pos):
		if self.board[from_pos] == '' or self.board[from_pos].color != 'white':
			raise MoveError()
		if len(get_pathway_cells()) > 0:
			raise MoveError()
		piece = self.board[from_pos]
		can = piece.can_move(from_pos, to_pos) if self.board[to_pos] == '' else piece.can_capture(from_pos, to_pos)
		if not can:
			raise MoveError()
		self.board[to_pos] = self.board[from_pos]
		self.board[from_pos] = ''

	def make_comp_move_0(self):
		from_pos, to_pos = self.comp.get_move()
		self.make_move(from_pos, to_pos)


	def make_move(self, from_pos, to_pos):
		print('current board:', self.board)
		if self.over:
			raise GameOverError

		if not self.is_correct_move(from_pos, to_pos):
			print(from_pos, to_pos, 'is incorrect move')
			self.print_board()
			raise MoveError

		if self.is_enpassant(from_pos, to_pos):
			self.board[to_pos[0]+from_pos[1]] = ''

		# if self.is_custeling(from_pos, to_pos):
			


		if isinstance(self.board[to_pos], King):
			self.over = True
			self.winner = 'Human' if self.board[to_pos].color == 'black' else 'Computer'
		self.board[to_pos] = self.board[from_pos]
		self.board[from_pos] = ''
		# print('end make move', self.board['a6'])
		# print(self.board)
		# self.save_session('ses.txt')
		if self.need_to_promote_pawn(to_pos):
			self.board[to_pos] = Queen(self.board[to_pos].color)
		# if self.board[to_pos]: #was en_passant

		self.last_moved[self.board[to_pos].color] = to_pos


	def need_to_promote_pawn(self, to_pos):
		if to_pos[1] != '1' and to_pos[1] != '8':
			return False
		piece = self.board[to_pos]
		if isinstance(piece, Pawn):
			return True
		return False

	def save_session(self, filename):
		if self.over:
			raise Exception
		with open(filename, 'w+') as f:
			for cell in self.board:
				piece = self.board[cell]
				str_format_piece = '{}("{}")'.format(type(piece).__name__, piece.color) if piece else '""'
				# print(str_format_piece)
				f.write("self.board['{}'] = {}\n".format(cell, str_format_piece))


	def load_session(self, filename='ses.txt'):
		# self.board = dict() # хз зачем оно, из-за него доска компа оставалась старой
		with open(filename) as f:
			r = f.read()
			lines = r.splitlines()
			# формат: self.board['a1'] = Pawn(white)
			for line in lines: 
				exec(line)



	def is_correct_move(self, from_pos, to_pos):
		if self.is_custeling(from_pos, to_pos):
			return True
		if self.is_enpassant(from_pos, to_pos):
			return True
		piece = self.board[from_pos]
		if piece == '':
			# print('piece=" "')
			# print(self.board)
			return False
		if self.board[to_pos] != '' and piece.color == self.board[to_pos].color:
			# print('atack self piece')
			return False

		can = piece.can_move(from_pos, to_pos) if self.board[to_pos] == '' else piece.can_capture(from_pos, to_pos)
		if not can:
			# print('not can move')
			return False
			
		# print('maybe barriers on pathway')
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
		if self.last_moved[self.board[enemy_pawn_place].color] != enemy_pawn_place:
			return False
		return True


	def make_en_passant_0(self, from_pos, to_pos):
		moved_pawn = self.board[from_pos]
		if not isinstance(moved_pawn, Pawn):
			raise MoveError
		if moved_pawn.color == 'white' and \
			(from_pos[1] != '5' or not moved_pawn.can_capture(from_pos, to_pos)):
			raise MoveError
		if moved_pawn.color == 'black' and \
			(from_pos[1] != '4' or not moved_pawn.can_capture(from_pos, to_pos)):
			raise MoveError
		if self.board[to_pos] != '':
			raise MoveError

		captured_pawn_place = to_pos[0]+from_pos[1]
		captured_pawn = self.board[captured_pawn_place]
		if not isinstance(captured_pawn, Pawn):
			raise MoveError

		self.board[to_pos] = self.board[from_pos]
		self.board[from_pos] = ''
		self.board[captured_pawn_place] = ''



	def is_special_method000(self, from_pos, to_pos):
		def is_custeling_0():
			return isinstance(self.board[from_pos], King) and \
						 isinstance(self.board[to_pos], Rook) and \
						( from_pos == 'e1' and (to_pos == 'a1' or to_pos == 'h1')  or \
						 from_pos == 'e8' and (to_pos == 'a8' or to_pos == 'h8')) and \
						not self.is_barrier_on_pathway(from_pos, to_pos)


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
		if from_pos != 'e1' or to_pos not in ['a1', 'h1']:
			return False
		if not isinstance(self.board[from_pos], King) or \
				not isinstance(self.board[to_pos], Rook):
			return False
		if self.is_barrier_on_pathway(from_pos, to_pos):
			return False
		return True



	def is_barrier_on_pathway(self, from_pos, to_pos):
		cells = self.get_pathway_cells(from_pos, to_pos)
		barriers = [self.board[c] for c in cells if not self.board[c] == '']
		print('PATHCELLS', cells)
		print('from_pos', from_pos, 'BARRIERS', barriers)
		return len(barriers) > 0


	def start_from_point(point_name):
		with open(point_name, 'r') as f:
			exec(f.read())

# ---------------------------
	# def save_session(self, filename):
	# 	with open(filename, 'w') as f:
	# 		cells = self.board.keys().sort() # board - simple dict
	# 		for cell in cells:
	# 			f.write('{}:{}'.format(cell, self.board[cell]))

	def print_board(self):
		for i in '87654321':
			s=''
			for j in 'abcdefgh':
				if self.board[j+i]:
					s+=str(self.board[j+i])
				else:
					s+=' '
			print(s)

	def print_comp_board(self):
		for i in '87654321':
			s=''
			for j in 'abcdefgh':
				if self.comp.board[j+i]:
					s+=str(self.comp.board[j+i])
				else:
					s+=' '
			print(s)

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
			else:
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


from collections import defaultdict


