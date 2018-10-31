
import sys
import os


from PyQt5.QtCore import (QByteArray, QDataStream, QIODevice, QMimeData,
		QPoint, Qt, QObject, QPointF, QPropertyAnimation, pyqtProperty,
		QParallelAnimationGroup, QSequentialAnimationGroup)
from PyQt5.QtGui import QColor, QDrag, QPainter, QPixmap, QPainterPath, QPalette
from PyQt5.QtWidgets import (QMainWindow, QApplication, QInputDialog, QCheckBox, QDialog,  QFrame, QHBoxLayout,
	QVBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QRadioButton, QToolButton, QComboBox, QWidget)

from game import *
from players import *
from QtCell import *
from QtBoard import *


class QtChess(QWidget):
	def __init__(self):
		super(QtChess, self).__init__()

	def setVisualBoard(self):
		horizontalLayout = QHBoxLayout()
		horizontalLayout.addWidget(self.board)
		self.setLayout(horizontalLayout)

	def try_make_move(self, from_pos, to_pos):
		pass

	def message_over(self, msg):
		buttonReply = QMessageBox.information(self, '', 'Game over\n'+msg, QMessageBox.Ok)
		if buttonReply == QMessageBox.Ok:
			# self.close()
			QApplication.quit()

	def load_session(self, ses_name='init'):
		self.game.load_session(ses_name)
		self.board.update()

	def save_session(self, ses_name):
		self.game.save_session(ses_name)


class QtGameWithComputer(QtChess):
	def __init__(self, hum_color='white'):
		super(QtGameWithComputer, self).__init__()

		hum_color = 'white'
		comp_color = 'black'

		self.game = LogicGame(t_clor=comp_color, b_color=hum_color)
		self.board = QtBoard(self)

		self.human = Player(hum_color)
		self.comp = Computer(self.game, comp_color)

		# self.acting_player = self.human if hum_color == 'white' else self.comp
		self.acting_player = self.human

		self.setWindowTitle('ChessWithComputer')
		# self.setAcceptDrops(True)
		self.setVisualBoard()
		self.show()

		# if 


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
			return

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
		super().message_over(pers_message)



class QtGameHotSeat(QtChess):
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
		# =====
		if self.game.is_in_check('white') or self.game.is_in_check('black'):
			self.message_over()
			# ===========

	def message_over(self):
		pers_message = 'Player with {} pieces has won!'.format(self.game.win_color)
		super().message_over(pers_message)




class QtGame(QWidget):
	def __init__(self, chess):
		super(QtGame, self).__init__()

		if not isinstance(chess, QtGameWithComputer) and not isinstance(chess, QtGameHotSeat):
			raise Exception()

		self.chess = chess
		horizontalLayout = QHBoxLayout()
		horizontalLayout.addWidget(self.chess)

		verticalLayout = QVBoxLayout()
		save_ses_btn = QPushButton('save', self)
		save_ses_btn.clicked.connect(self.save_btn_func)
		verticalLayout.addWidget(save_ses_btn)
		load_ses_btn = QPushButton('load', self)
		load_ses_btn.clicked.connect(self.load_btn_func)
		verticalLayout.addWidget(load_ses_btn)

		horizontalLayout.addLayout(verticalLayout)

		self.setLayout(horizontalLayout)
		self.setWindowTitle('Chess')
		self.show()


	def save_btn_func(self): 
		text, okPressed = QInputDialog.getText(self, "Save session", "Enter session name:", QLineEdit.Normal, "")
		if okPressed and text != '':
			self.chess.save_session(text)

	def load_btn_func(self):
		sessions = self.get_sessions_files()
		ses_name, okPressed = QInputDialog.getItem(self, "Load session", "Saved session:", sessions, 0, False)
		if okPressed and ses_name:
			self.chess.load_session(ses_name)
		
	def get_sessions_files(self):
		dirname = 'saved_sessions'
		files = os.listdir(dirname)
		return [filename[:-4] for filename in files]


class MenuWidget(QWidget):
	def __init__(self):
		super(MenuWidget, self).__init__()
		verticalLayout = QVBoxLayout()

		# choose one or two
		self.one_player_radio = QRadioButton('one player')
		self.one_player_radio.setChecked(True)
		self.two_player_radio = QRadioButton('two player')
		# self.one_player_radio.toggled.connect(lambda:self.two_player_radio.setChecked(not self.one_player_radio.isChecked()))
		# self.two_player_radio.toggled.connect(lambda:self.one_player_radio.setChecked(not self.two_player_radio.isChecked()))
		verticalLayout.addWidget(self.one_player_radio)
		verticalLayout.addWidget(self.two_player_radio)

		# set color (if play with computer)
		horizontalLayout = QHBoxLayout()
		self.color_inf = QFrame()
		self.color_inf.setStyleSheet('border: 1px solid black; background-color:white;')
		supported_frame = QFrame() # for other elements don't move when hide

		self.change_color_btn = QPushButton('change my color')
		def change_clr():
			if self.color_inf.palette().color(QPalette.Background).name() == '#ffffff':
				self.color_inf.setStyleSheet('border: 1px solid black; background-color:black;')
			else:
				self.color_inf.setStyleSheet('border: 1px solid black; background-color:white;')
		self.change_color_btn.clicked.connect(change_clr)
		# self.black_color_btn.clicked.connect()

		horizontalLayout.addWidget(self.color_inf)
		horizontalLayout.addWidget(self.change_color_btn)
		horizontalLayout.addWidget(supported_frame)
		verticalLayout.addLayout(horizontalLayout)

		# to hide color choice if two players
		def hide_or_show_choice_clr():
			self.color_inf.setHidden(not self.color_inf.isHidden())
			self.change_color_btn.setHidden(not self.change_color_btn.isHidden())
		self.two_player_radio.toggled.connect(lambda:hide_or_show_choice_clr())

		# add special features
		self.modes = QComboBox()
		self.modes.addItems(['Classic mode', 'With radioactive knights', 'Maharajah'])
		verticalLayout.addWidget(self.modes)

		# start button
		self.start_btn = QPushButton('Start')
		self.start_btn.clicked.connect(self.start_game_mode)
		verticalLayout.addWidget(self.start_btn)

		self.setLayout(verticalLayout)
		self.show()

	def start_game_mode(self):
		# возвращает нужный объект - игру 
		self.hide()

		game = QtGameWithComputer() if (self.one_player_radio.isChecked()) else QtGameHotSeat()
		self.game = QtGame(game)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	# game = QtGameWithComputer()
	# game = QtGameHotSeat()
	# chess = QtChess()
	wind = MenuWidget()
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
