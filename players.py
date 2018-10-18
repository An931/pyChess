# from board import *
import random 


# игроки. у человека только его цвет
# у компьютера вся логика его хода

# изменить: убрать дублирование доски (сделать в место этого полем игру)
# класс move убрать или изменить


class Player:
	pass


class Computer():
	def __init__(self, game):
		self.board = game.board
		self.game = game
		self.color = 'black'

		# self.move_num = 1

	def get_move(self):
		# move = self.get_sorted_movements()[0]

		# if isinstance(self.board.board[move[1]], Empty):
		# 	return self.get_random_movement()

		# print(move.from_pos, move.to_pos)
		
		# if self.move_num == 1:
		# 	self.move_num = 2
		# 	return 'a7', 'a6'

		# elif self.move_num == 2:
		# 	self.move_num = 3
		# 	return 'a6', 'a5'

		return self.get_random_movement()

	def get_random_movement(self):
		moves = self.get_all_movements()
		r1 = random.randint(0, len(moves)-1)
		from_pos = list(moves.keys())[r1]
		r2 = random.randint(0, len(moves[from_pos])-1)
		# return (from_pos, moves[from_pos][r2])
		res = (from_pos, moves[from_pos][r2])
		return res

	def get_sorted_movements(self):
		""" возвращает список ходов (tuple), упорядоченных по выгоде"""
		# не работает т.к. доска уже просто словарь
		# ДОДЕЛАТЬ
		candidats_to_move = self.get_all_movements()
		moves = []
		for c in candidats_to_move:
			for m in candidats_to_move[c]:
				moves.append(Move(c, m, self.board))
		moves.sort(key=lambda x: x.benefit, reverse=True)
		return [m.move for m in moves]

	def get_all_movements(self):
		""" возвращает словарь ходов {from : all where} """
		candidats_to_move = {}
		for cell, piece in self.board.items():
			if piece and piece.color == self.color:
				movements = self.get_movments_of_piece(cell)
				if len(movements) > 0:
					candidats_to_move[cell] = movements
		return candidats_to_move

	def get_movments_of_piece(self, id): 
		"""возвращает все возможные ходы данной фигуры"""
		# if not self.board[id] or self.board[id].color != self.color:
		# 	return 
		piece = self.board[id]
		empty, enemy = self.get_empty_or_enemy_cells()
		all_to_pos = empty + enemy
		moves = [to_pos for to_pos in all_to_pos if self.game.is_correct_move(id, to_pos)]
		return moves

	def get_empty_or_enemy_cells(self):
		""" возвр тапл списков: все пустые и все клетки противника"""
		empty = []
		enemy = []
		for c in self.board.keys():
			piece = self.board[c]
			if not piece:
				empty.append(c)
			elif piece.color != self.color:
				enemy.append(c)
		return (empty, enemy)

	def is_correct_move(self, from_pos, to_pos):
		piece = self.board[from_pos]
		if piece == '':
			return False
		if self.board[to_pos] != '' and piece.color == self.board[to_pos].color:
			return False

		can = piece.can_move(from_pos, to_pos) if self.board[to_pos] == '' else piece.can_capture(from_pos, to_pos)
		if not can:
			return False
		return not self.is_barrier_on_pathway(from_pos, to_pos)


	def is_barrier_on_pathway(self, from_pos, to_pos):
		cells = get_pathway_cells(from_pos, to_pos)
		barriers = [self.board[c] for c in cells if not self.board[c] == '']
		return len(barriers) > 0

def get_pathway_cells(from_pos, to_pos): 
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
		min_num = int(min(from_pos[1], to_pos[1]))
		min_let = ord(min(from_pos[0], to_pos[0]))
		cells = []
		for i in range(1, delta):
			l = min_let + i
			n = min_num + i
			cells.append(chr(l)+str(n))
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

class Move():
	def __init__(self, from_pos, to_pos, board):
		self.from_pos = from_pos
		self.to_pos = to_pos
		self.board = board
		self.simple_evaluate()
		self.move = (from_pos, to_pos)

	def simple_evaluate(self):
		self.benefit = self.board.board[self.to_pos].weight

	def evaluate(self):
		pass

