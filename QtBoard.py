import sys
import os


from PyQt5.QtCore import (QByteArray, QDataStream, QIODevice, QMimeData,
		QPoint, Qt, QObject, QPointF, QPropertyAnimation, pyqtProperty,
		QParallelAnimationGroup, QSequentialAnimationGroup)
from PyQt5.QtGui import QColor, QDrag, QPainter, QPixmap, QPainterPath, QMovie
from PyQt5.QtWidgets import (QMainWindow, QApplication, QInputDialog , QFrame, QHBoxLayout,
	QVBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QWidget)

from game import *
from players import *
from QtCell import *

class QtBoard(QWidget):
	def __init__(self, game, parent=None):
		super(QtBoard, self).__init__(parent)
		self.game = game.game #OPASNO
		# self.game = game #OPASNO
		verticalLayout = QVBoxLayout()
		for y in '87654321':
			horizontalLayout = QHBoxLayout()
			for x in 'abcdefgh':
				horizontalLayout.addWidget(QtCell(x+y, game, self))
				verticalLayout.addLayout(horizontalLayout)
		self.setLayout(verticalLayout)
		# self.setAcceptDrops(True)

		self.setToolTip('board')
		# self.setGeometry(200, 200, 500, 500)

		self.moved_piece = None
		# для custeling:
		self.moved_king = None
		self.moved_rook = None
		self.put_pieces()

	def put_pieces(self):
		# ставит фигуры в соответствие со своей логической доской
		for row in self.layout().children():
			for cell in [row.itemAt(i).widget() for i in range(8)]:
				logic_piece = self.game.board[cell.id]
				if logic_piece:
					cell.set_piece(type(logic_piece).__name__, logic_piece.color)
				else:
					cell.del_piece()

	def update(self):
		if self.moved_piece:
			self.moved_piece.hide()
			self.moved_piece = None
		if self.moved_king:
			self.moved_king.hide()
			self.moved_king = None
		if self.moved_rook:
			self.moved_rook.hide()
			self.moved_rook = None
		self.put_pieces()
		if self.game.over:
			self.parent().message_over()
			return
		self.update_radioactive()
		# self.update_incheck_highlits()
		self.highlight_if_incheck()

	def make_human_move000(self, from_pos, to_pos):
		self.game.make_move(from_pos, to_pos)

		from_cell = self.get_cell(from_pos)
		to_cell = self.get_cell(to_pos)

		if self.is_custeling(from_pos, to_pos):
			self.animate_custeling(from_pos, to_pos)
			from_cell.del_piece()
			to_cell.del_piece()

		else:
			to_cell.set_piece(from_cell.piece.name, from_cell.piece.color)
			from_cell.del_piece()
			self.update()

		# self.update()
		self.make_computer_move()

	def make_computer_move00(self):
		from_pos, to_pos = self.comp.get_move()
		self.game.make_move(from_pos, to_pos)
		self.animate_move(from_pos, to_pos)

		from_cell = self.get_cell(from_pos)
		from_cell.del_piece()

	def animate_move(self, from_pos, to_pos):
		from_pos_coords = self.get_coords(from_pos)
		to_pos_coords = self.get_coords(to_pos)

		from_cell = self.get_cell(from_pos)

		# необходимо чтобы скрывать его в mouse_press
		# иначе при наведении нельзя поставить фигуру на нее
		self.moved_piece = QtPiece(from_cell.piece.name, from_cell.piece.color, self)
		self.moved_piece.to_cell = self.get_cell(to_pos)

		from_cell.del_piece()

		self.anim = QPropertyAnimation(self.moved_piece, b'pos')
		self.anim.setDuration(1000) # speed

		self.anim.setStartValue(from_pos_coords)
		self.anim.setEndValue(to_pos_coords)
		self.anim.start()
		self.anim.finished.connect(self.update)

	def is_custeling000(self, from_pos, to_pos):
		# проверяет только позиции
		return from_pos in ['e1', 'e8'] and to_pos in ['a1', 'h1', 'a8', 'h8']

	def animate_custeling(self, from_pos, to_pos):
		n = from_pos[1] # 1 or 8
		rook_future_place = 'f'+str(n) if to_pos == 'h'+str(n) else 'd'+str(n)
		king_future_place = 'g'+str(n) if to_pos == 'h'+str(n) else 'c'+str(n)

		color = self.get_piece(from_pos).color

		self.moved_king = QtPiece('King', color, self)
		self.moved_king.to_cell = self.get_cell(king_future_place)
		self.moved_rook = QtPiece('Rook', color, self)
		self.moved_rook.to_cell = self.get_cell(rook_future_place)

		self.king_anim = QPropertyAnimation(self.moved_king, b'pos')
		self.king_anim.setDuration(1000) # speed
		self.king_anim.setStartValue(self.get_coords(from_pos))
		self.king_anim.setEndValue(self.get_coords(king_future_place))
		self.king_anim.start()

		self.rook_anim = QPropertyAnimation(self.moved_rook, b'pos')
		self.rook_anim.setDuration(1000)  # speed
		self.rook_anim.setStartValue(self.get_coords(to_pos))
		self.rook_anim.setEndValue(self.get_coords(rook_future_place))
		self.rook_anim.start()

		self.get_cell(from_pos).del_piece()
		self.get_cell(to_pos).del_piece()

		self.rook_anim.finished.connect(self.update)

	def get_cell(self, id):
		for row in self.layout().children():
			for cell in [row.itemAt(i).widget() for i in range(8)]:
				if cell.id == id:
					return cell

	def get_piece(self, id):
		return self.get_cell(id).piece

	def get_coords(self, cell_id):
		# возвращает координаты центра конкретной клетки относительно доски в пикселях
		return self.get_cell(cell_id).pos()

	def update_radioactive(self):
		# pass
		# пробегается по клеткам (лог или гуи) и подсвечивает либо делает как было
		for cell in self.game.board:
			# if cell in self.game.radioactive_cells:
			if self.game.board[cell]:
				continue
			for tup in self.game.last_from_poses:
				if tup[0] == cell and tup[1]:
					self.get_cell(cell).highlight()
					break
				else:
					self.get_cell(cell).highlight(False)

	def update_incheck_highlghts00(self):
		white_in_check = self.game.is_in_check('white')
		black_in_check = self.game.is_in_check('black')
		for row in self.layout().children():
			for cell in [row.itemAt(i).widget() for i in range(8)]:
				if cell.piece and cell.piece.name == 'King':
					if cell.piece.color == 'white':
						if white_in_check: 
							cell.highlight_incheck(True)
						else:
							cell.highlight_incheck(False)
					else:
						if black_in_check: 
							cell.highlight_incheck(True)
						else:
							cell.highlight_incheck(False)

	def highlight_piece(self, from_pos):
		piece = self.get_cell(from_pos).piece
		if not piece:
			return
		piece.setPixmap(QPixmap('pieces_img/{}_King_incheck.png'.format(piece.color[0])).scaled(50, 50))
		# piece.setPixmap(QPixmap('pieces_img/r_King.png').scaled(50, 50))
		# piece.setPixmap(piece.origin_pixmap)

	def blink_piece00(self, from_pos):
		# cell = self.get_cell(from_pos)
		# blinked_piece = QtPiece('King', 'red', cell)
		# blinked_piece.hide()
		piece = self.get_cell(from_pos).piece
		movie = QMovie("pieces_img/r_King.gif")
		# movie = QMovie("pieces_img/with_menu.gif")
		movie.setScaledSize(piece.size())

		piece.setMovie(movie)
		movie.start()

	def highlight_if_incheck(self):
		incheck_king_poses = self.game.get_incheck_king_positions()
			# highlite king !!
		for pos in incheck_king_poses:
			self.highlight_piece(pos)

