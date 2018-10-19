PIECES = {'white': {'Rook': '♖', 'Knight': '♘', 'Bishop': '♗', 'Queen': '♕', 'King': '♔', 'Pawn': '♙'}, 
					'black': {'Rook': '♜', 'Knight': '♞', 'Bishop': '♝', 'Queen': '♛', 'King': '♚', 'Pawn': '♟'},
					'no': {'Empty': '⿴'}} # other symbols for empty: ۞ ※ ▓ ░ ⛚ ⛋ ❏ ⿴

# используется для хранения фигур - опр цвета, значимости и характеристики хода

# у каждой фигуры есть цвет, вес, методы может сходить и ударить
# у всех кроме пешки ударить = сходить


class Piece(object):
	def __init__(self, type, color, weight):
		self.type = type 
		self.color = color
		self.weight = weight

	def can_move(self, start, to): 
		raise NotImplementedError

	def can_capture(self, start, to):
		return self.can_move(start, to) 

	def __repr__(self):
		return '{} {}'.format(self.color, self.type)

	def __str__(self):
		return PIECES[self.color][self.type]


class Rook(Piece):
	def __init__(self, color):
		super().__init__('Rook', color, 2)

	def can_move(self, start, to):
		dx = ord(start[0]) - ord(to[0])
		dy = int(start[1]) - int(to[1])
		return dx == 0 and dy != 0 or \
						dx != 0 and dy == 0


class Knight(Piece):
	def __init__(self, color):
		super().__init__('Knight', color, 2)
		self = Pawn('white')

	def can_move(self, start, to):
		dx = abs(ord(start[0]) - ord(to[0]))
		dy = abs(int(start[1]) - int(to[1]))
		return dx == 2 and dy == 1 or \
						dx == 1 and dy == 2


class Bishop(Piece):
	def __init__(self, color):
		super().__init__('Bishop', color, 2)

	def can_move(self, start, to):
		dx = ord(start[0]) - ord(to[0])
		dy = int(start[1]) - int(to[1])
		return abs(dx) == abs(dy)


class Queen(Piece):
	def __init__(self, color):
		super().__init__('Queen', color, 5)

	def can_move(self, start, to):
		dx = abs(ord(start[0]) - ord(to[0]))
		dy = abs(int(start[1]) - int(to[1]))
		return (dx == dy) or (dx == 0 and dy != 0)\
							 or (dx != 0 and dy == 0)


class King(Piece):
	def __init__(self, color):
		super().__init__('King', color, 6)

	def can_move(self, start, to):
		dx = abs(ord(start[0]) - ord(to[0]))
		dy = abs(int(start[1]) - int(to[1]))
		return dx <= 1 and dy <= 1 and not (dx == 0 and dy == 0)


class Pawn(Piece): 
	def __init__(self, color):
		super().__init__('Pawn', color, 1)
		self.direction = 'up' if color == 'white' else 'down'

	def can_move(self, start, to): 
		if self.direction == 'up':
			dy = int(to[1]) - int(start[1])
		else:
			dy = int(start[1]) - int(to[1])
		dx = ord(start[0]) - ord(to[0])

		if self.direction == 'up' and start[1] == '2' or\
				self.direction == 'down' and start[1] == '7':
			return dx == 0 and (dy == 1 or dy == 2)
		return dx == 0 and dy == 1

	def can_capture(self, start, to):
		if self.direction == 'up':
			dy = int(to[1]) - int(start[1])
		else:
			dy = int(start[1]) - int(to[1])
		dx = abs(ord(start[0]) - ord(to[0]))
		return dx == 1 and dy == 1


class Empty:
	def __init__(self):
		self.type = 'Empty'
		self.color = 'no'
		self.weight = 0
