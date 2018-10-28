import sys
import os


from PyQt5.QtCore import (QByteArray, QDataStream, QIODevice, QMimeData,
		QPoint, Qt, QObject, QPointF, QPropertyAnimation, pyqtProperty,
		QParallelAnimationGroup, QSequentialAnimationGroup)
from PyQt5.QtGui import QColor, QDrag, QPainter, QPixmap, QPainterPath
from PyQt5.QtWidgets import (QMainWindow, QApplication, QInputDialog , QFrame, QHBoxLayout,
	QVBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QWidget)

from game import *
from players import *
from QtCell import *


class QtBoard_OLD_VERSION(QWidget):
	def __init__(self, game, parent=None):
		super(QtBoard, self).__init__(parent)
		self.game = game
		self.comp = Computer(game)

		verticalLayout = QVBoxLayout()
		# verticalLayout.addStretch()
		for y in '87654321':
			horizontalLayout = QHBoxLayout()
			# horizontalLayout.addStretch()
			for x in 'abcdefgh':
				horizontalLayout.addWidget(QtCell(x+y, self.game, self))
				verticalLayout.addLayout(horizontalLayout)
		self.setLayout(verticalLayout)
		self.setAcceptDrops(True)

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


	def make_human_move(self, from_pos, to_pos):
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

	def make_computer_move(self):
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

		self.anim = QPropertyAnimation(self.moved_piece, b'pos')
		self.anim.setDuration(1000) # speed

		self.anim.setStartValue(from_pos_coords)
		self.anim.setEndValue(to_pos_coords)
		self.anim.start()
		self.anim.finished.connect(self.update)

	def is_custeling(self, from_pos, to_pos):
		# проверяет только позиции
		return from_pos == 'e1' and to_pos in ['a1', 'h1']

	def animate_custeling(self, from_pos, to_pos):
		if not self.is_custeling(from_pos, to_pos):
			raise Exception()
		# _1 так как рокировка только у человека
		rook_future_place = 'f1' if to_pos == 'h1' else 'd1'
		king_future_place = 'g1' if to_pos == 'h1' else 'c1'

		self.moved_king = QtPiece('King', 'white', self)
		self.moved_king.to_cell = self.get_cell(king_future_place)
		self.moved_rook = QtPiece('Rook', 'white', self)
		self.moved_rook.to_cell = self.get_cell(rook_future_place)

		self.king_anim = QPropertyAnimation(self.moved_king, b'pos')
		self.king_anim.setDuration(1000) # speed
		self.king_anim.setStartValue(self.get_coords('e1'))
		self.king_anim.setEndValue(self.get_coords(king_future_place))
		self.king_anim.start()

		self.rook_anim = QPropertyAnimation(self.moved_rook, b'pos')
		self.rook_anim.setDuration(1000)  # speed
		self.rook_anim.setStartValue(self.get_coords(to_pos))
		self.rook_anim.setEndValue(self.get_coords(rook_future_place))
		self.rook_anim.start()

	def get_cell(self, id):
		for row in self.layout().children():
			for cell in [row.itemAt(i).widget() for i in range(8)]:
				if cell.id == id:
					return cell

	def get_coords(self, cell_id):
		# возвращает координаты центра конкретной клетки относительно доски в пикселях
		return self.get_cell(cell_id).pos()

	def update(self):
		if self.game.over:
			self.message_over()
			return

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

	def message_over(self):
		pers_message = 'You won!' if self.game.winner == 'Human' else 'You lost!'
		buttonReply = QMessageBox.information(self, '', 'Game over\n'+pers_message, QMessageBox.Ok)
		if buttonReply == QMessageBox.Ok:
			self.parent().close()

	def mousePressEvent0(self, event):
		# self.game.print_board()
		# self.update()
		pass


	def load_session(self, ses_name='init'):
		self.game.load_session(ses_name)
		self.update()

	def save_session(self, ses_name):
		self.game.save_session(ses_name)

class QtBoard(QWidget):
	def __init__(self, game, parent=None):
		super(QtBoard, self).__init__(parent)
		self.game = game.game #OPASNO

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

		self.anim = QPropertyAnimation(self.moved_piece, b'pos')
		self.anim.setDuration(1000) # speed

		self.anim.setStartValue(from_pos_coords)
		self.anim.setEndValue(to_pos_coords)
		self.anim.start()
		self.anim.finished.connect(self.update)

	def is_custeling(self, from_pos, to_pos):
		# проверяет только позиции
		return from_pos in ['e1', 'e8'] and to_pos in ['a1', 'h1', 'a8', 'h8']

	def animate_custeling(self, from_pos, to_pos):
		if not self.is_custeling(from_pos, to_pos):
			raise Exception()

		n = from_pos[1] # 1 or 8
		rook_future_place = 'f'+str(n) if to_pos == 'h'+str(n) else 'd'+str(n)
		king_future_place = 'g'+str(n) if to_pos == 'h'+str(n) else 'c'+str(n)

		self.moved_king = QtPiece('King', 'white', self)
		self.moved_king.to_cell = self.get_cell(king_future_place)
		self.moved_rook = QtPiece('Rook', 'white', self)
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

	def update(self):
		if self.game.over:
			self.message_over()
			return

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


class QtGameWithComputer00(QWidget):
	def __init__():
		super(QtGameWithComputer00, self).__init__()
		self.human = Player()
		self.comp = Computer()
		self.game = Game()
		self.qtboard = QtBoard()


class QtGameHotSeat(QWidget):
	def __init__(self):
		super(QtGameHotSeat, self).__init__()
		self.human_w = Player('white')
		self.human_b = Player('black')
		self.game = LogicGame()
		self.board = QtBoard(self)

		self.acting_player = self.human_w

		self.setWindowTitle('HotSeat')
		# self.setAcceptDrops(True)

		self.setVisualBoard()
		self.show()

	def setVisualBoard(self):
		horizontalLayout = QHBoxLayout()
		horizontalLayout.addWidget(self.board)
		self.setLayout(horizontalLayout)


	def try_make_move(self, from_pos, to_pos):
		if self.game.over:
			raise GameOverError
		# if self.board.get_piece(from_pos).color != self.acting_player.color:
		# 	return
		if not self.game.is_correct_move(from_pos, to_pos):
			return

		self.game.make_move(from_pos, to_pos)

		if self.board.is_custeling(from_pos, to_pos):
			self.board.animate_custeling(from_pos, to_pos)
			from_cell = self.board.get_cell(from_pos)
			to_cell = self.board.get_cell(to_pos)
			from_cell.del_piece()
			to_cell.del_piece()

		else:
			# to_cell.set_piece(from_cell.piece.name, from_cell.piece.color)
			# from_cell.del_piece()
			self.board.update()

		if self.game.over:
			self.message_over()

		self.acting_player = self.human_w if self.acting_player == self.human_b else self.human_b


	def message_over(self):
		pers_message = 'You won!' if self.game.winner == 'Human' else 'You lost!'
		buttonReply = QMessageBox.information(self, '', 'Game over\n'+pers_message, QMessageBox.Ok)
		if buttonReply == QMessageBox.Ok:
			self.parent().close()


	def load_session(self, ses_name='init'):
		self.game.load_session(ses_name)
		self.board.update()

	def save_session(self, ses_name):
		self.game.save_session(ses_name)



class QtChess(QWidget):
	def __init__(self):
		super(QtChess, self).__init__()

		horizontalLayout = QHBoxLayout()
		game = LogicGame()
		self.board = QtBoard(game, self)
		horizontalLayout.addWidget(self.board)

		verticalLayout = QVBoxLayout()
		save_ses_btn = QPushButton('save', self)
		save_ses_btn.clicked.connect(self.save_btn_func)
		verticalLayout.addWidget(save_ses_btn)
		load_ses_btn = QPushButton('load', self)
		load_ses_btn.clicked.connect(self.load_btn_func)
		verticalLayout.addWidget(load_ses_btn)

		horizontalLayout.addLayout(verticalLayout)

		self.setLayout(horizontalLayout)
		self.show()

	def save_btn_func(self):
		text, okPressed = QInputDialog.getText(self, "Save session", "Enter session name:", QLineEdit.Normal, "")
		if okPressed and text != '':
			self.board.save_session(text)

	def load_btn_func(self):
		sessions = self.get_sessions_files()
		ses_name, okPressed = QInputDialog.getItem(self, "Load session", "Saved session:", sessions, 0, False)
		if okPressed and ses_name:
			self.board.load_session(ses_name)
		
	def get_sessions_files(self):
		dirname = 'saved_sessions'
		files = os.listdir(dirname)
		return [filename[:-4] for filename in files]

	def mousePressEvent(self, event):
		# нажатие именно на фигуру
		child = self.childAt(event.pos())
		print(isinstance(child, QtPiece))


if __name__ == '__main__':
	app = QApplication(sys.argv)
	chess = QtGameHotSeat()
	sys.exit(app.exec_())

	# -----------------------
	# app = QApplication(sys.argv)
	# mainWidget = QWidget()
	# horizontalLayout = QHBoxLayout()
	# board = QtBoard(mainWidget)
	# horizontalLayout.addWidget(board)

	# verticalLayout = QVBoxLayout()
	# save_ses_btn = QPushButton('save', mainWidget)
	# save_ses_btn.clicked.connect(board.save_session)
	# verticalLayout.addWidget(save_ses_btn)
	# load_ses_btn = QPushButton('load', mainWidget)
	# load_ses_btn.clicked.connect(board.load_session)
	# verticalLayout.addWidget(load_ses_btn)

	# horizontalLayout.addLayout(verticalLayout)

	# mainWidget.setLayout(horizontalLayout)
	# mainWidget.show()
	# sys.exit(app.exec_())
	# -----------------------------------------

