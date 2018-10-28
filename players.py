import random 
from pieces import *

class Player:
	def __init__(self, color):
		# self.board = game.board
		# self.game = game
		if color not in ['white', 'black']:
			raise Exception
		self.color = color

class Computer:
	def __init__(self, game, color):
		self.board = game.board
		self.game = game
		if color not in ['white', 'black']:
			raise Exception
		self.color = color

	def get_move(self):
		# print(move.from_pos, move.to_pos)
		# return self.get_random_movement()

		move = self.get_sorted_movements()[0]
		if not self.board[move[1]] and not self.game.is_enpassant(*move):
			# чтобы ходы в начале игры не были одинаковыми 
			return self.get_random_movement()
		return move

	def get_random_movement(self):
		moves = self.get_all_movements()
		r1 = random.randint(0, len(moves)-1)
		from_pos = list(moves.keys())[r1]
		r2 = random.randint(0, len(moves[from_pos])-1)
		res = (from_pos, moves[from_pos][r2])
		return res

	def get_sorted_movements(self):
		""" возвращает список ходов (tuple), упорядоченных по выгоде"""
		candidats_to_move = self.get_all_movements()  # словарь ходов {from : all where}
		moves = []
		for from_pos in candidats_to_move:
			for to_pos in candidats_to_move[from_pos]:
				moves.append(Move(from_pos, to_pos, self.board))
		moves.sort(key=lambda x: x.benefit, reverse=True)
		return [(m.from_pos, m.to_pos) for m in moves]

	def get_all_movements(self):
		""" возвращает словарь ходов {from : all where} """
		candidats_to_move = {}
		for cell, piece in self.board.items():
			if piece and piece.color == self.color:
				movements = self.get_movments_of_piece(cell)
				if len(movements) > 0:
					candidats_to_move[cell] = movements
		return candidats_to_move

	def get_movments_of_piece(self, cell_id): 
		"""возвращает все возможные ходы данной фигуры"""
		piece = self.board[cell_id]
		empty, enemy = self.get_empty_or_enemy_cells()
		all_to_pos = empty + enemy
		moves = [to_pos for to_pos in all_to_pos if self.game.is_correct_move(cell_id, to_pos)]
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


