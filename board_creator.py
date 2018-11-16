from pieces import *


class BoardCreator:
	def create_board(t_color, b_color, radioactive):
		board = dict()
		for x in 'abcdefgh':
			for y in '12345678':
				board[x+y] = BoardCreator.get_piece(x, y, t_color, b_color, radioactive)
		return board

	def get_piece(x, y, t_color, b_color, radioactive=False):
		if y == '2':
			return Pawn(b_color, 'up')
		if y == '7':
			return Pawn(t_color, 'down')
		if y == '1':
			# color = b_color
			return BoardCreator.get_strong_piece(x, b_color, radioactive)
		if y == '8':
			# color = t_clor
			return BoardCreator.get_strong_piece(x, t_color, radioactive)
		return ''

	def get_strong_piece(x, color, radioactive_knights):
		if x == 'a' or x == 'h':
			return Rook(color)
		if x == 'b' or x == 'g':
			# return Knight(color)
			return Knight(color, radioactive=radioactive_knights)
		if x == 'c' or x == 'f':
			return Bishop(color)
		if x == 'd':
			return Queen(color)
		if x == 'e':
			return King(color)

	def get_maharajah_board(t_color, b_color, mah_color, mah_pos):
		board = dict()
		if mah_pos[1] not in ['1', '2', '7', '8']:
			raise Exception('wrong Maharajah position')

		if mah_pos[1] in '12':
			for x in 'abcdefgh':
				for y in '345678':
					board[x+y] = BoardCreator.get_piece(x, y, t_color, b_color)
				for y in '12':
					board[x+y] = ''

		else:
			for x in 'abcdefgh':
				for y in '123456':
					board[x+y] = BoardCreator.get_piece(x, y, t_color, b_color)
				for y in '78':
					board[x+y] = ''

		board[mah_pos] = Maharajah(mah_color)
		return board

	def create_board_from_file(filename):
		board = BoardCreator.create_empty_board()
		with open(filename) as f:
			r = f.read()
			lines = r.splitlines()
			# формат line: self.board['a1'] = Pawn(white)
			for line in lines: 
				exec(line)
		return board

	def create_empty_board():
		board = dict()
		for x in 'abcdefgh':
			for y in '12345678':
				board[x+y] = ''
		return board
