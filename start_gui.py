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
from QtBoard import *




class QtGameWithComputer(QWidget):
	def __init__(self, hum_color='white'):
		super(QtGameWithComputer, self).__init__()
		self.game = LogicGame()
		self.board = QtBoard(self)

		self.human = Player(hum_color)
		comp_color = 'black' if (hum_color == 'white') else 'white'
		self.comp = Computer(self.game, comp_color)

		# self.acting_player = self.human if hum_color == 'white' else self.comp
		self.acting_player = self.human

		self.setWindowTitle('ChessWithComputer')
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

		if not self.game.is_correct_move(from_pos, to_pos):
			return

		if self.game.is_custeling(from_pos, to_pos):
			self.game.make_move(from_pos, to_pos)
			self.board.animate_custeling(from_pos, to_pos)
			from_cell = self.board.get_cell(from_pos)
			to_cell = self.board.get_cell(to_pos)
			from_cell.del_piece()
			to_cell.del_piece()

		else:
			self.game.make_move(from_pos, to_pos)
			# to_cell.set_piece(from_cell.piece.name, from_cell.piece.color)
			# from_cell.del_piece()
			self.board.update()

		if self.game.over:
			self.message_over()

		# self.acting_player = self.comp
		self.make_comp_move()

	def make_comp_move(self):

		from_pos, to_pos = self.comp.get_move()

		if not self.game.is_correct_move(from_pos, to_pos):
			return

		if self.game.is_custeling(from_pos, to_pos):
			pass # пока компьютер все равно не умеет в рокировку
		# 	self.game.make_move(from_pos, to_pos)
		# 	self.board.animate_custeling(from_pos, to_pos)
		# 	from_cell = self.board.get_cell(from_pos)
		# 	to_cell = self.board.get_cell(to_pos)
		# 	from_cell.del_piece()
		# 	to_cell.del_piece()

		else:
			self.game.make_move(from_pos, to_pos)
			# to_cell.set_piece(from_cell.piece.name, from_cell.piece.color)

			# from_cell.del_piece()
			self.board.animate_move(from_pos, to_pos)
			# self.board.update() # это в методе доски

		if self.game.over:
			self.message_over()

		# self.acting_player = self.human_w

	def message_over(self):
		pers_message = 'You won!' if (self.game.win_color == self.human.color) else 'You lost :('
		buttonReply = QMessageBox.information(self, '', 'Game over\n'+pers_message, QMessageBox.Ok)
		if buttonReply == QMessageBox.Ok:
			# self.close()
			QApplication.quit()


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

		if self.game.is_custeling(from_pos, to_pos):
			self.game.make_move(from_pos, to_pos)
			self.board.animate_custeling(from_pos, to_pos)
			# это должно быть в методе анимации 
			# from_cell = self.board.get_cell(from_pos)
			# to_cell = self.board.get_cell(to_pos)
			# from_cell.del_piece()
			# to_cell.del_piece()

		else:
			self.game.make_move(from_pos, to_pos)
			# to_cell.set_piece(from_cell.piece.name, from_cell.piece.color)
			# from_cell.del_piece()

			self.board.update()

		if self.game.over:
			self.message_over()

		self.acting_player = self.human_w if self.acting_player == self.human_b else self.human_b

	def message_over(self):
		pers_message = 'Player with {} pieces has won!'.format(self.game.win_color)
		buttonReply = QMessageBox.information(self, '', 'Game over\n'+pers_message, QMessageBox.Ok)
		if buttonReply == QMessageBox.Ok:
			# self.close()
			QApplication.quit()

	def load_session00(self, ses_name='init'):
		self.game.load_session(ses_name)
		self.board.update()

	def save_session00(self, ses_name):
		self.game.save_session(ses_name)



class QtChess00(QWidget):
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
	chess = QtGameWithComputer()
	# chess = QtGameHotSeat()
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

