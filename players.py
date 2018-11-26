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
		print(self.color)

	def get_moveMBFASTER(self):
		moves = self.game.get_sorted_movements(self.color, avoid_mate=False)
		if not moves:
			return
		move, i = moves[0], 0
		while self.game.will_be_mate(*move):
			i += 1
			move = moves[i]
		if not self.board[move[1]] and not self.game.is_enpassant(*move): # чтобы ходы в начале игры не были одинаковыми
			random.shuffle(moves)
			return moves[0]
		return move

	def get_move(self):
		moves = self.game.get_sorted_movements(self.color)
		if not moves:
			return
		move = moves[0]
		if not self.board[move[1]] and not self.game.is_enpassant(*move):
			# чтобы ходы в начале игры не были одинаковыми 
			# return self.get_random_movement()
			random.shuffle(moves)
			return moves[0]
		return move

	def get_random_movement(self):
		moves = self.game.get_all_movements(self.color)
		r1 = random.randint(0, len(moves)-1)
		from_pos = list(moves.keys())[r1]
		r2 = random.randint(0, len(moves[from_pos])-1)
		res = (from_pos, moves[from_pos][r2])
		return res

	def will_be_mate00(self, from_pos, to_pos):
		# return False
		# if not self.game.is_correct_move(from_pos, to_pos) or not isinstance(self.board[from_pos], King):
		if not self.game.is_correct_move(from_pos, to_pos):
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
