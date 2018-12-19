import random 
import copy
from pieces import *
from game import *
import time

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
		# print(self.color)

	def get_move_MBFASTER(self):
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
		start_time = time.time()
		pseudo_game = self.game.get_pseudo_game()
		root_node = Node(None, pseudo_game, '')
		first_level_nodes = root_node.get_children()
		print('first_level_nodes ', time.time()-start_time)
		second_level_nodes = []
		i=0
		for node in first_level_nodes:
			second_level_nodes += node.get_children()
			print(i, 'of second_level_nodes ', time.time()-start_time)
			i+=1
		second_level_nodes.sort(key=lambda x: x.evaluation, reverse=True)
		for node in second_level_nodes:
			print(node)
		return second_level_nodes[0].get_first_move()

		# moves = self.game.get_sorted_movements(self.color)
		# if not moves:
		# 	return
		# move = moves[0]
		# if not self.board[move[1]] and not self.game.is_enpassant(*move):
		# 	# чтобы ходы в начале игры не были одинаковыми 
		# 	# return self.get_random_movement()
		# 	random.shuffle(moves)
		# 	return moves[0]
		# return move

	def get_move_OLD(self):
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

	def get_random_movement000(self):
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

	# ---------------------

	def evaluate_position(game):
		pass

	def get_best_move(moves):
		# оценивает каждый ход на какую то глубину, выдает наилучший
		pass


class AI:
	def evaluate_position00(board):
		# !!!!!! максимум - для хорошего хода черных, минмум для белых
		evaluation = 0
		for cell in board:
			piece = board[cell]
			if piece:
				if piece.color == 'black':
					evaluation += piece.weight
				else:
					evaluation -= piece.weight
		return evaluation

	def evaluate_position(game):
		# !!!!!! максимум - для хорошего хода черных, минмум для белых
		evaluation = 0
		for cell in game.board:
			piece = game.board[cell]
			if piece:
				if piece.color == 'black':
					evaluation += piece.weight
				else:
					evaluation -= piece.weight
		return evaluation

class DesisionTree:
	def __init__(self, game, color):
		self.origin_game = game
		self.player_color = color
		# см, возможно здесь избавляться от проверки на мат
		self.possible_moves = game.get_sorted_movements(color)

class Node:
# узел имеет игру, ход нашего игрока и ход соперника (единственный и оптимальный)
	def __init__(self, parent, game, move):
		self.parent = parent
		self.move = move # ход, который привел к узлу, пустой если корень
		self.game = game #pseudo game ---- 
		# move - last move of this game
		# self.enemy_move = game.get_sorted_movements(game.b_color, True)
		if move: # то есть если это не корень - хз зачем, мб вообще убрать корень
			if not self.game.over:
				self.game.make_move(*move, False)
				self.enemy_move = game.get_sorted_movements(game.b_color, False)[0]
				if not self.game.over:
					self.game.make_move(*self.enemy_move, False)

		self.evaluation = Node.evaluate_position(game)
		# здесь проверка на законченность игры и мб альфа-бета
		# если надо, продолжить и найти детей
		# self.children = self.get_children() #list of Nodes

	def open00(self):
		self.children = self.get_children()

	def get_children(self):
		moves = self.game.get_sorted_movements(self.game.t_color, False)
		children = []
		for move in moves:
			new_game = self.game.get_pseudo_game()
			# new_game.make_move(*move)
			new_child = Node(self, new_game, move)
			children.append(new_child)
		self.children = children
		return children

	def get_first_move(self):
		node = self
		while node.parent:
			prev_node = node
			node = node.parent
		return prev_node.move

	def __str__(self):
		res='Node, '
		node = self
		moves_list=[]
		while node.parent:
			moves_list.append(' enemy : '+str(node.enemy_move))
			moves_list.append(' my: '+str(node.move))
			# prev_node = node
			node = node.parent
		moves_list.reverse()
		res+=str(moves_list)
		res+=' end evaluation '+str(self.evaluation)
		return res

	def evaluate_position(game):
		if game.over:
			if game.win_color == game.t_color:
				return 1000
			else:
				return -100
		evaluation = 0
		for cell in game.board:
			piece = game.board[cell]
			if piece:
				if piece.color == game.t_color:
					evaluation += piece.weight
				else:
					evaluation -= piece.weight
		return evaluation



