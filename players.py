import random 
import copy
from pieces import *
from game import *

class Player:
	def __init__(self, color):
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
		move = self.game.get_sorted_movements(self.color)[0]
		if not self.board[move[1]] and not self.game.is_enpassant(*move):
			# чтобы ходы в начале игры не были одинаковыми 
			return self.get_random_movement()
		return move

	def get_random_movement(self):
		moves = self.game.get_all_movements(self.color)
		r1 = random.randint(0, len(moves)-1)
		from_pos = list(moves.keys())[r1]
		r2 = random.randint(0, len(moves[from_pos])-1)
		res = (from_pos, moves[from_pos][r2])
		return res

	# def get_sorted_movements(self):
	# 	""" возвращает список ходов (tuple), упорядоченных по выгоде"""
	# 	candidats_to_move = self.get_all_movements()  # словарь ходов {from : all where}
	# 	moves = []
	# 	for from_pos in candidats_to_move:
	# 		for to_pos in candidats_to_move[from_pos]:
	# 			if not self.will_be_mate(from_pos, to_pos):
	# 				moves.append(Move(from_pos, to_pos, self.board))
	# 			# moves.append(Move(from_pos, to_pos, self.board))
	# 	moves.sort(key=lambda x: x.benefit, reverse=True)
	# 	return [(m.from_pos, m.to_pos) for m in moves]

	# def get_all_movements(self):
	# 	""" возвращает словарь ходов {from : all where} """
	# 	candidats_to_move = {}
	# 	for cell, piece in self.board.items():
	# 		if piece and piece.color == self.color:
	# 			movements = self.get_movments_of_piece(cell)
	# 			if len(movements) > 0:
	# 				candidats_to_move[cell] = movements
	# 	return candidats_to_move

	# def get_movments_of_piece(self, cell_id): 
	# 	"""возвращает все возможные ходы данной фигуры"""
	# 	piece = self.board[cell_id]
	# 	# empty, enemy = self.get_empty_or_enemy_cells()
	# 	# all_to_pos = empty + enemy
	# 	moves = [to_pos for to_pos in self.game.board if self.game.is_correct_move(cell_id, to_pos)]
	# 	return moves

	def will_be_mate(self, from_pos, to_pos):
		# return False
		if not self.game.is_correct_move(from_pos, to_pos) or not isinstance(self.board[from_pos], King):
			return False
		game = self.game.get_pseudo_game()
		game.make_move(from_pos, to_pos)
		if game.is_in_check(self.color):
			return True
		return False

	def want_draw(self):
		my_pieces=[]
		enemy_pieces=[]
		for cell in self.board:
			piece = self.board[cell]
			if piece and not isinstance(piece, Pawn):
				if piece.color == self.color:
					my_pieces.append(piece)
				else:
					enemy_pieces.append(piece)
		my_pieces.sort(key=lambda x: x.weight, reverse=True)
		enemy_pieces.sort(key=lambda x: x.weight, reverse=True)
		if len(enemy_pieces)-len(my_pieces) > 4:
			return True
		if len(my_pieces) < 3 or my_pieces[1].weight<5:
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

