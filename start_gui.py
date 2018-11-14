
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
from saver import *

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

	def load_session(self, ses_name):
		pass

	def save_session(self, ses_name):
		Saver.save_session(ses_name, self.game)

	def load_session00(self, ses_name='init'):
		self.game.load_session(ses_name)
		self.board.update()

	def save_session000(self, ses_name):
		self.game.save_session(ses_name)


class QtGameWithComputer(QtChess):
	def __init__(self, hum_color='white', radioactive=False, maharajah = False):
		super(QtGameWithComputer, self).__init__()

		comp_color = 'black' if hum_color == 'white' else 'white'

		self.game = LogicGame(comp_color, hum_color, radioactive, maharajah)
		self.board = QtBoard(self)

		self.human = Player(hum_color)
		self.comp = Computer(self.game, comp_color)

		self.acting_player = self.human if hum_color == 'white' else self.comp

		self.setWindowTitle('ChessWithComputer')
		self.setVisualBoard()
		self.show()

		if self.acting_player == self.comp:
			self.make_comp_move()


	def try_make_move(self, from_pos, to_pos):
		if self.game.over:
			raise GameOverError

		if not self.game.is_correct_move(from_pos, to_pos):
			return

		if self.game.is_custeling(from_pos, to_pos):
			self.game.make_move(from_pos, to_pos)
			self.board.animate_custeling(from_pos, to_pos)
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
			return

		self.acting_player = self.comp
		self.parent.update_incheck_msg()
		self.make_comp_move()

	def make_comp_move(self):

		from_pos, to_pos = self.comp.get_move()

		if not self.game.is_correct_move(from_pos, to_pos):
			return

		if self.game.is_custeling(from_pos, to_pos):
			self.board.animate_custeling(from_pos, to_pos)
		else:
			self.board.animate_move(from_pos, to_pos)

		self.game.make_move(from_pos, to_pos)
		# to_cell.set_piece(from_cell.piece.name, from_cell.piece.color)

		# from_cell.del_piece()


		if self.game.over:
			self.message_over()

		self.acting_player = self.human
		self.parent.update_incheck_msg()

	def message_over(self):
		pers_message = 'You won!' if (self.game.win_color == self.human.color) else 'You lost :('
		super().message_over(pers_message)

	def load_session(self, ses_name):
		# self.game.board = None
		game = Saver.load_session(ses_name)
		self.game = game
		self.comp.game = game
		self.board.game = game
		# print(self.game.board)
		self.human = Player(game.b_color)
		self.comp = Computer(self.game, game.t_color)

		# мб не нужно, так как комп всегда успеет сходить 
		last_act_color = game.board[game.history[-1][1]].color
		self.acting_player = self.human if self.comp.color == last_act_color else self.comp
		# self.acting_player = self.human if self. == 'white' else self.comp
		self.board.update()
		if self.acting_player == self.comp:
			self.make_comp_move()


class QtGameHotSeat(QtChess):
	def __init__(self, radioactive=False, maharajah=False):
		super(QtGameHotSeat, self).__init__()
		self.human_w = Player('white')
		self.human_b = Player('black')
		self.game = LogicGame('black', 'white', radioactive, maharajah)
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
		self.parent.update_incheck_msg()
		# =====
		# сбщ если шах
		# if self.game.is_in_check('white') or self.game.is_in_check('black'):
		# 	self.message_over()
			# ===========

	def message_over(self):
		pers_message = 'Player with {} pieces has won!'.format(self.game.win_color)
		super().message_over(pers_message)

	def load_session(self, ses_name):
		# self.game.board = None
		game = Saver.load_session(ses_name)
		self.game = game
		self.board.game = game
		# print(self.game.board)

		last_act_color = game.board[game.history[-1][1]].color
		self.acting_player = self.human_w if last_act_color == 'black' else self.human_b
		# self.acting_player = self.human if self. == 'white' else self.comp
		self.board.update()


class QtGame(QWidget):
	def __init__(self, chess):
		super(QtGame, self).__init__()

		if not isinstance(chess, QtGameWithComputer) and not isinstance(chess, QtGameHotSeat):
			raise Exception()

		self.chess = chess
		# self.in_check_msg = QLabel('Here would be msg\n if King is in check     ')
		self.in_check_msg = QLabel('                                 ')
		save_ses_btn = QPushButton('save', self)
		save_ses_btn.clicked.connect(self.save_btn_func)
		load_ses_btn = QPushButton('load', self)
		load_ses_btn.clicked.connect(self.load_btn_func)
		# save_ses_btn.setMaximumSize(50, 10)
		# load_ses_btn.setMaximumSize(50, 10)


		horizontalLayout = QHBoxLayout()
		verticalLayout = QVBoxLayout()

		verticalLayout.addWidget(load_ses_btn)
		verticalLayout.addWidget(save_ses_btn)
		verticalLayout.addWidget(self.in_check_msg)

		horizontalLayout.addWidget(self.chess)
		horizontalLayout.addLayout(verticalLayout)

		self.setLayout(horizontalLayout)
		self.setWindowTitle('Chess')
		# self.setMouseTracking(True)
		self.show()

	def update_incheck_msg(self):
		msg1 = 'white King is in check' if self.chess.game.is_in_check('white') else ''
		msg2 = 'black King is in check' if self.chess.game.is_in_check('black') else ''
		self.in_check_msg.setText(msg1+'\n'+msg2)


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
		dirname = 'sessions'
		files = os.listdir(dirname)
		return [filename[:-7] for filename in files]

	def get_sessions_files00(self):
		dirname = 'saved_sessions'
		files = os.listdir(dirname)
		return [filename[:-4] for filename in files]

class MenuWidget(QWidget):
	def __init__(self):
		super(MenuWidget, self).__init__()
		self.verticalLayout = QVBoxLayout()
		self.add_player_count_radio()
		self.add_change_color()
		self.add_modes()
		self.add_choice_mah_position()
		self.add_start_btn()

		self.setLayout(self.verticalLayout)
		self.setMinimumSize(400, 300)
		self.show()

	def start_game_mode(self):
		# создает (начинает) нужный объект - игру 
		self.hide()
		# combo box --currentText()

		# play with computer
		if self.one_player_radio.isChecked(): 
			hum_color = self.change_color_btn.text()
			if self.modes.currentText() == 'Radioactive knights':
				game = QtGameWithComputer(hum_color, radioactive=True)
			elif self.modes.currentText() == 'Maharajah':
				mah_pos = self.mah_pos.currentText()
				# mah_color = self.change_color_btn.text() # при игре с компом цвет Магараджи совпадает с цветом игрока
				mah_color = self.mah_color.text()
				game = QtGameWithComputer(hum_color, maharajah=(mah_color, mah_pos))
			else:
				game = QtGameWithComputer(hum_color)

		else:
			if self.modes.currentText() == 'Radioactive knights':
				game = QtGameHotSeat(adioactive=True)
			elif self.modes.currentText() == 'Maharajah':
				mah_pos = self.mah_pos.currentText()
				mah_color = self.mah_color.text()
				game = QtGameHotSeat(aharajah=(mah_color, mah_pos))
			else:
				game = QtGameHotSeat()

		self.game = QtGame(game)
		game.parent = self.game

	def add_player_count_radio(self):
		self.one_player_radio = QRadioButton('One player (play with Computer)')
		self.one_player_radio.setChecked(True)
		self.two_player_radio = QRadioButton('Two players')
		# self.one_player_radio.toggled.connect(lambda:self.two_player_radio.setChecked(not self.one_player_radio.isChecked()))
		# self.two_player_radio.toggled.connect(lambda:self.one_player_radio.setChecked(not self.two_player_radio.isChecked()))
		self.verticalLayout.addWidget(self.one_player_radio)
		self.verticalLayout.addWidget(self.two_player_radio)

	def add_change_color(self):
		horizontalLayout = QHBoxLayout()
		supported_frame = QFrame() # for other elements don't move when hide

		self.change_color_btn = QPushButton()
		self.change_color_btn.setText('white')
		self.change_color_btn.setToolTip('Click to change your color')
		def change_clr():
			if self.change_color_btn.text() == 'white':
				self.change_color_btn.setText('black')
				# self.change_color_btn.setStyleSheet('border: 1px solid black; background-color:black;')
			else:
				self.change_color_btn.setText('white')
				# self.change_color_btn.setStyleSheet('border: 1px solid black; background-color:white;')
		self.change_color_btn.clicked.connect(lambda: (change_clr(), self.change_mah_clr()))
		# self.change_color_btn.clicked.connect(change_clr)
		self.change_color_text = QLabel('Your color:   ')
		horizontalLayout.addWidget(self.change_color_text)
		horizontalLayout.addWidget(self.change_color_btn)
		horizontalLayout.addWidget(supported_frame)

		self.verticalLayout.addLayout(horizontalLayout)
		self.add_hide_color_choice()

	def add_hide_color_choice(self):
		def hide_or_show_choice_clr():
			self.change_color_btn.setHidden(not self.change_color_btn.isHidden())
			self.change_color_text.setHidden(not self.change_color_text.isHidden())
		self.two_player_radio.toggled.connect(hide_or_show_choice_clr)

	def add_modes(self):
		# add special features
		self.modes = QComboBox()
		self.modes.addItems(['Classic mode', 'Radioactive knights', 'Maharajah'])
		self.verticalLayout.addWidget(self.modes)


	def change_mah_clr(self):
		self.mah_pos.clear()
		mah_color = 'white' if self.mah_color.text() == 'black' else 'black'
		self.mah_color.setText(mah_color)
		if self.mah_color.text() == self.change_color_btn.text():
			self.mah_pos.addItems(['a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1', 'a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2'])
		else:
			self.mah_pos.addItems(['a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7', 'a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8'])
			# self.change_color_btn.setStyleSheet('border: 1px solid black; background-color:white;')

	def add_choice_mah_position(self):

		horizontalLayout = QHBoxLayout()
		self.mah_pos = QComboBox()
		self.mah_pos.addItems(['a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1', 'a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2'])
		self.mah_color = QPushButton(self.change_color_btn.text()) # depend of radiobut
		self.mah_color.clicked.connect(self.change_mah_clr)
		self.mah_color.setToolTip('Click to change Maharajah color')
		self.mah_pos.setToolTip('Choose Maharajah first position')
		supported_frame = QFrame()
		self.mah_text = QLabel('Maharajah position and color:   ')
		horizontalLayout.addWidget(self.mah_text)
		horizontalLayout.addWidget(self.mah_pos)
		horizontalLayout.addWidget(self.mah_color)
		horizontalLayout.addWidget(supported_frame)
		self.verticalLayout.addLayout(horizontalLayout)

		self.mah_pos.hide()
		self.mah_text.hide()
		self.mah_color.hide()
		self.add_hide_mah_choice()


	def add_hide_mah_choice(self):
		# to hide choose maharajah position
		def hide_or_show_choose_mah_pos():
			if self.modes.currentText() == 'Maharajah':
				self.mah_pos.show()
				self.mah_text.show()
				self.mah_color.show()
				# if self.two_player_radio.isChecked(): # так комп не может играть за mah
				# 	self.mah_color.show()
			else:
				self.mah_pos.hide()
				self.mah_text.hide()
				self.mah_color.hide()
		self.modes.currentIndexChanged.connect(hide_or_show_choose_mah_pos)


	def add_start_btn(self):
		self.verticalLayout.addSpacing(100)
		# start button
		self.start_btn = QPushButton('Start')
		self.start_btn.clicked.connect(self.start_game_mode)
		self.verticalLayout.addWidget(self.start_btn)


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
