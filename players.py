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

	def get_move(self):
		start_time = time.time()
		time_limit = 3
		pseudo_game = self.game.get_pseudo_game()
		root_node = Node(None, pseudo_game, '')
		first_level_nodes = root_node.get_children()
		second_level_nodes = []
		for node in first_level_nodes:
			second_level_nodes += node.get_children()
			print('second_level_nodes ', time.time()-start_time)
		second_level_nodes.sort(key=lambda x: x.evaluation, reverse=True)
		# for node in second_level_nodes:
		# 	print(node)
		# return second_level_nodes[0].get_first_move()

		third_level_nodes=[]
		for node in second_level_nodes:
			third_level_nodes += node.get_children()
			print('of third_level_nodes ', time.time()-start_time)
			if time.time()-start_time > time_limit:
				break
		third_level_nodes.sort(key=lambda x: x.evaluation, reverse=True)
		# to print tree solution
		for node in third_level_nodes:
			print(node)
		# to make some interesting
		equivalent_nodes = [n for n in third_level_nodes if n.evaluation==third_level_nodes[0].evaluation]
		random.shuffle(equivalent_nodes)
		return equivalent_nodes[0].get_first_move()


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


class Node:
# узел имеет игру, ход нашего игрока и ход соперника (единственный и оптимальный)
	def __init__(self, parent, game, move):
		self.parent = parent
		self.move = move 
		self.enemy_move = ''
		self.game = game #pseudo game ---- 
		if move: 
			if not self.game.over:
				self.game.make_move(*move, False)
				self.enemy_move = game.get_sorted_movements(game.b_color, False)[0]
				if not self.game.over:
					self.game.make_move(*self.enemy_move, False)

		self.evaluation = Node.evaluate_position(game)


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



