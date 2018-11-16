PIECES = {'white': {'Rook': '♖', 'Knight': '♘', 'Bishop': '♗', 'Queen': '♕', 'King': '♔', 'Pawn': '♙'},
					'black': {'Rook': '♜', 'Knight': '♞', 'Bishop': '♝', 'Queen': '♛', 'King': '♚', 'Pawn': '♟'},
					'no': {'Empty': '⿴'}}  # other symbols for empty: ۞ ※ ▓ ░ ⛚ ⛋ ❏ ⿴


class Piece(object):
		def __init__(self, type, color, weight, radioactive=False):
				if color not in ['white', 'black']:
					raise Exception()
				self.type = type
				self.color = color
				self.weight = weight
				self.already_moved = False
				# if radioactive and not isinstance(self, Knight):
				# 	raise Exception('cold work incorrect')
				self.radioactive = radioactive

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
				super().__init__('Rook', color, 5)

		def can_move(self, start, to):
				dx = ord(start[0]) - ord(to[0])
				dy = int(start[1]) - int(to[1])
				return dx == 0 and dy != 0 or \
							 dx != 0 and dy == 0


class Knight(Piece):
		def __init__(self, color, radioactive=False):
				super().__init__('Knight', color, 3, radioactive)

		def can_move(self, start, to):
				dx = abs(ord(start[0]) - ord(to[0]))
				dy = abs(int(start[1]) - int(to[1]))
				return dx == 2 and dy == 1 or \
							 dx == 1 and dy == 2


class Bishop(Piece):
		def __init__(self, color):
				super().__init__('Bishop', color, 3)

		def can_move(self, start, to):
				dx = ord(start[0]) - ord(to[0])
				dy = int(start[1]) - int(to[1])
				return abs(dx) == abs(dy)


class Queen(Piece):
		def __init__(self, color):
				super().__init__('Queen', color, 9)

		def can_move(self, start, to):
				dx = abs(ord(start[0]) - ord(to[0]))
				dy = abs(int(start[1]) - int(to[1]))
				return (dx == dy) or (dx == 0 and dy != 0) \
							 or (dx != 0 and dy == 0)


class King(Piece):
		def __init__(self, color):
				super().__init__('King', color, 10)

		def can_move(self, start, to):
				dx = abs(ord(start[0]) - ord(to[0]))
				dy = abs(int(start[1]) - int(to[1]))
				return dx <= 1 and dy <= 1 and not (dx == 0 and dy == 0)


class Pawn(Piece):
		def __init__(self, color, direction):
				super().__init__('Pawn', color, 1)
				if direction not in ['up', 'down']:
					raise Exception()
				self.direction = direction

		def can_move(self, start, to):
				if self.direction == 'up':
						dy = int(to[1]) - int(start[1])
				else:
						dy = int(start[1]) - int(to[1])
				dx = ord(start[0]) - ord(to[0])

				if self.direction == 'up' and start[1] == '2' or \
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


class Maharajah(Piece):
		def __init__(self, color):
				super().__init__('Maharajah', color, 10)

		def can_move(self, start, to):
				knight = Knight(self.color)
				queen = Queen(self.color)
				return knight.can_move(start, to) or queen.can_move(start, to)
