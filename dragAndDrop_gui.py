import sys
# from datetime import datetime

from PyQt5.QtCore import (QByteArray, QDataStream, QIODevice, QMimeData,
		QPoint, Qt, QObject, QPointF, QPropertyAnimation, pyqtProperty, 
		QParallelAnimationGroup, QSequentialAnimationGroup)
from PyQt5.QtWidgets import (QMainWindow, QApplication, QFrame, QHBoxLayout, 
	QVBoxLayout, QLabel, QPushButton, QWidget)

from game import *
from players import *
import time


class QtPiece(QLabel):
	def __init__(self, name, color, parent=None):
		pixmap = QPixmap('pieces/{}.png'.format(color[0]+'_'+name))
		pixmap = pixmap.scaled(50, 50)
		super(QLabel, self).__init__(parent)
		self.setPixmap(pixmap)
		self.setMinimumSize(50, 50)

		self.name = name
		self.color = color
		self.show()



class QtCell(QFrame):
	def __init__(self, id, game, parent, piece=None):
		super(QtCell, self).__init__(parent)
		self.game = game
		self.piece = None
		self.id = id
		self.board = parent
		self.setColor()

		self.setMinimumSize(50, 50)
		self.setLineWidth(10)
		self.setAcceptDrops(True)


	def put_new_piece(self, piece_name, piece_color):
		if self.piece:
			self.piece.hide()
		if not piece_name:
			self.piece = None
		else:
			self.piece = QtPiece(piece_name, piece_color, self)
			# self.piece.show()


	def setColor(self):
		if self.id[0] in 'aceg' and self.id[1] in '1357'\
			or self.id[0] in 'bdfh' and self.id[1] in '2468':
			self.setStyleSheet('background-color:black;')
			self.color = 'black'
		else:
			self.setStyleSheet('background-color:white;')
			self.color = 'white'

	def dragEnterEvent(self, event):
		# print('drag')
		# return
		# event.accept()

		if event.source() == self:
			event.accept()
		else:
			# наведение на дугие клетки
			# здесь можно высчитывать возможность хода
			# либо для каждой кл заново, либо сразу сост спсок возм-ых и искать кл в этом списке
			event.acceptProposedAction()

	def dropEvent_REALMETHOD_0(self, event):
		# if self.icon:
		#     self.icon.hide()
		try:
			self.game.make_move(event.source().id, self.id)
			self.piece.hide()
			newPiece = QtPiece(event.source().piece.name, event.source().piece.color, self)
			newPiece.show()
			self.piece = newPiece

			# перемещение иконки
			event.setDropAction(Qt.MoveAction)
			event.accept()
			if event.source() == self:
				pass
			else:
				pass
				# return
				# coords = event.source().coords
				# analyse if move correct
		except:
			print('wrong move')
			return

		self.parent().make_computer_move()


	def dropEvent_0(self, event):
		# проверка на все спец методы (вроде 2 шт + становление ферзем)
		from_pos = event.source().id
		to_pos = self.id

		# ВЫНЕСТИ ЭТО В QTBOARD
		if self.game.is_correct_custeling(from_pos, to_pos):
			rook_place = 'f1' if to_pos == 'h1' else 'd1'
			king_place = 'g1' if to_pos == 'h1' else 'c1'

			self.board.animate_move(from_pos, king_place)
			self.board.animate_move(to_pos, rook_place)
			self.board.animate_move('a1', 'a2')

			# ???????????????????????????
			animationGroup = QParallelAnimationGroup()
			animationGroup.addAnimation(self.board.animate_move(from_pos, king_place))
			animationGroup.addAnimation(self.board.animate_move(to_pos, rook_place))
			animationGroup.start()
			return


		self.game.make_move(from_pos, to_pos)
		# print('DROP', type(self.piece), self.id)
		if self.piece:
			self.piece.hide()
		newPiece = QtPiece(event.source().piece.name, event.source().piece.color, self)
		# newPiece.show()
		self.piece = newPiece

		# перемещение иконки
		event.setDropAction(Qt.MoveAction)
		event.accept()

		# if event.source() == self:
		#     pass
		# else:
		#     pass

		self.board.make_computer_move()

	def dropEvent(self, event):
		# проверка на все спец методы (вроде 2 шт + становление ферзем)
		from_pos = event.source().id
		to_pos = self.id

		if self.game.is_correct_custeling()

		self.board.make_move(from_pos, to_pos, True)

		# ВЫНЕСТИ ЭТО В QTBOARD
		# if self.game.is_correct_custeling(from_pos, to_pos):
		#     rook_place = 'f1' if to_pos == 'h1' else 'd1'
		#     king_place = 'g1' if to_pos == 'h1' else 'c1'

		#     self.board.animate_move(from_pos, king_place)
		#     self.board.animate_move(to_pos, rook_place)
		#     self.board.animate_move('a1', 'a2')

		#     # ???????????????????????????
		#     animationGroup = QParallelAnimationGroup()
		#     animationGroup.addAnimation(self.board.animate_move(from_pos, king_place))
		#     animationGroup.addAnimation(self.board.animate_move(to_pos, rook_place))
		#     animationGroup.start()
		#     return

		# перемещение иконки
		event.setDropAction(Qt.MoveAction)
		event.accept()

		# if event.source() == self:
		#     pass
		# else:
		#     pass

		# self.board.make_computer_move()


	def mousePressEvent(self, event):
		# костыль - фигуры пропадают когда возникает след.нажатие
		# сделать это после анимации (хз как)
		if self.parent().moved_piece:
			self.parent().moved_piece.hide()
			to_cell = self.parent().moved_piece.to_cell
			print('!!!!!!!!', self.parent().moved_piece.name, self.parent().moved_piece.color)
			to_cell.piece = QtPiece(self.parent().moved_piece.name, self.parent().moved_piece.color, to_cell)
			self.parent().moved_piece = None

		child = self.childAt(event.pos())
		if not child:
			return
		if child.color == 'black':
			return

		pixmap = QPixmap(child.pixmap())

		itemData = QByteArray()
		dataStream = QDataStream(itemData, QIODevice.WriteOnly)
		dataStream << pixmap << QPoint(event.pos() - child.pos())

		mimeData = QMimeData()
		mimeData.setData('application/x-dnditemdata', itemData)

		drag = QDrag(self)
		drag.setMimeData(mimeData)
		drag.setPixmap(pixmap)
		drag.setHotSpot(event.pos() - child.pos())

		# затемняет лейбл
		# доделать чтобы фигура пропадала
		# как вариант: заполнять цветом таким же как клетка 
		tempPixmap = QPixmap(pixmap)
		painter = QPainter()
		painter.begin(tempPixmap)
		painter.fillRect(pixmap.rect(), QColor(127, 127, 127, 127))
		# painter.fillRect(pixmap.rect(), QColor())
		painter.end()

		child.setPixmap(tempPixmap)

		if drag.exec_(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction) == Qt.MoveAction:
			# если перемещение в доступное место
			child.close()
		else:
			# child.show()
			child.setPixmap(pixmap)


class QtBoard(QWidget):
	def __init__(self, parent=None):
		super(QtBoard, self).__init__(parent)
		self.game = Game()

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

		self.setWindowTitle('board')
		# self.setGeometry(200, 200, 500, 500)
		# self.show()
		self.put_pieces()

		self.moved_piece = None
		# self.anim = None

	def put_pieces_0DoesntDependOnGameBoard(self, saved_session=None):
		if saved_session:
			print('not implemet')
			raise Exception()

		for row in self.layout().children():
			# print(row)
			# print(row.children()) # why [] ?
			for cell in [row.itemAt(i).widget() for i in range(8)]:
				# print(cell.id)
				if cell.id[1] in '1278':
					cell.put_new_piece(*self.get_init_piece(cell))
				# cell.add_new_icon(self.get_init_piece(cell))

	def put_pieces(self):
		for row in self.layout().children():
			# print(row)
			# print(row.children()) # why [] ?
			for cell in [row.itemAt(i).widget() for i in range(8)]:
				# print(cell.id)
				# print(self.game.board[cell.id])
				if cell.piece:
					cell.piece.hide()
				logic_piece = self.game.board[cell.id]
				if logic_piece:
				  cell.put_new_piece(type(logic_piece).__name__, logic_piece.color)
				# if cell.id[1] in '1278':
				#     cell.put_new_piece(*self.get_init_piece(cell))
				# cell.add_new_icon(self.get_init_piece(cell))

	def get_init_piece_000(self, cell):
		# if cell_id.id[1] not in '1278':
		#     return None
		if cell.id[1] == '2':
			return 'Pawn', 'white'
		if cell.id[1] == '7':
			return 'Pawn', 'black'
		if cell.id[1] == '1':
			if cell.id[0] == 'a' or cell.id[0] == 'h':
				return 'Rook', 'white'
			if cell.id[0] == 'b' or cell.id[0] == 'g':
				return 'Knight', 'white'
			if cell.id[0] == 'c' or cell.id[0] == 'f':
				return 'Bishop', 'white'
			if cell.id[0] == 'd':
				return 'Queen', 'white'
			if cell.id[0] == 'e':
				return 'King', 'white'
		if cell.id[1] == '8':
			if cell.id[0] == 'a' or cell.id[0] == 'h':
				return 'Rook', 'black'
			if cell.id[0] == 'b' or cell.id[0] == 'g':
				return 'Knight', 'black'
			if cell.id[0] == 'c' or cell.id[0] == 'f':
				return 'Bishop', 'black'
			if cell.id[0] == 'd':
				return 'Queen', 'black'
			if cell.id[0] == 'e':
				return 'King', 'black'
		print('get_init_piece', 'hui')
		return 'a', 'n'


	def get_init_piece_0(self, cell):
		if cell.id[1] == '2':
			return 'w_Pawn'
		if cell.id[1] == '7':
			return 'b_Pawn'
		if cell.id[1] == '1':
			if cell.id[0] == 'a' or cell.id[0] == 'h':
				return 'w_Rook'
			if cell.id[0] == 'b' or cell.id[0] == 'g':
				return 'w_Knight'
			if cell.id[0] == 'c' or cell.id[0] == 'f':
				return 'w_Bishop'
			if cell.id[0] == 'd':
				return 'w_Queen'
			if cell.id[0] == 'e':
				return 'w_King'
		if cell.id[1] == '8':
			if cell.id[0] == 'a' or cell.id[0] == 'h':
				return 'b_Rook'
			if cell.id[0] == 'b' or cell.id[0] == 'g':
				return 'b_Knight'
			if cell.id[0] == 'c' or cell.id[0] == 'f':
				return 'b_Bishop'
			if cell.id[0] == 'd':
				return 'b_Queen'
			if cell.id[0] == 'e':
				return 'b_King'


	def promote_pawn(self, to_pos):
		if to_pos[1] != '1' and to_pos[1] != '8':
			return
		logic_piece = self.game.board[to_pos]
		if isinstance(logic_piece, Pawn):
			self.game.board[to_pos] = Queen(logic_piece.color)
			qt_cell = self.get_cell(to_pos)
			qt_cell.put_new_piece('Queen', logic_piece.color)


	def make_move(self, from_pos, to_pos, was_hum=False):
		# self.game.print_board()
		# ЗДЕСЬ ПРОВЕРКА НА СПЕЦ МЕТОДЫ

		self.game.make_move(from_pos, to_pos)

		from_cell = self.get_cell(from_pos)
		to_cell = self.get_cell(to_pos)

		to_cell.put_new_piece(from_cell.piece.name, from_cell.piece.color)
		from_cell.put_new_piece(None, None)

		self.promote_pawn(to_pos)
		# костыль
		if was_hum:
			self.make_computer_move()

	def make_computer_move(self):
		from_pos, to_pos = self.game.comp.get_move()
		self.animate_move(from_pos, to_pos)
		# animation

		# end animation


		self.game.make_move(from_pos, to_pos)

		from_cell = self.get_cell(from_pos)
		to_cell = self.get_cell(to_pos)

		# to_cell.put_new_piece(from_cell.piece.name, from_cell.piece.color)
		from_cell.put_new_piece(None, None)


	def animate_move(self, from_pos, to_pos):
		# ОСТАВИТЬ ТОЛЬКО АНИМАЦИЮ, ПРОДУМАТЬ КАК ЕЕ СКРЫВАТЬ, УБРАТЬ(?) ИЗ АТРИБУТА В ПРОСТО ПЕРЕМЕННУЮ

		# нужно: переместить label, убрать атр piece с клетки from, добавить на клетку to
		from_pos_coords = self.get_coords(from_pos)
		to_pos_coords = self.get_coords(to_pos)
		# self.path.lineTo(*to_pos_coords)

		from_cell = self.get_cell(from_pos)
		# print(from_pos)
		# from_cell.piece.hide()
		self.moved_piece = QtPiece(from_cell.piece.name, from_cell.piece.color, self)
		# from_cell.piece = None
		self.moved_piece.to_cell = self.get_cell(to_pos)

		# self.get_cell(to_pos).piece = moved_piece
		# self.get_cell(to_pos).piece = QtPiece(piece.name, piece.color, self.get_cell(to_pos))

		# if self.anim:
		#     self.anim.stop()

		self.anim = QPropertyAnimation(self.moved_piece, b'pos')
		self.anim.setDuration(1000) # speed
		
		self.anim.setStartValue(from_pos_coords)
		self.anim.setEndValue(to_pos_coords)
		# self.anim.setEndValue(QPointF(*to_pos_coords))

		self.anim.start()
		# self.anim.stop()
		# return self.anim


		# это должно быть здесь но будет в cell.mousepress
		# self.moved_piece.hide()

		# self.anim = QPropertyAnimation(self.moved_piece, b'pos')




	def get_cell(self, id):
		for row in self.layout().children():
			for cell in [row.itemAt(i).widget() for i in range(8)]:
				if cell.id == id:
					return cell




	def get_coords(self, cell_id):
		# возвращает координаты центра конкретной клетки относительно доски в пикселях
		return self.get_cell(cell_id).pos()

	def mousePressEvent(self, event):
		print('boooard')
		self.game.print_board()
		# self.game.print_comp_board()

	def load_session(self):
		self.game.load_session()
		self.put_pieces()

	def save_session(self):
		self.game.save_session('ses.txt'


class QtGame_0:
	def __init__(self):
		pass



class QtChess_000(QMainWindow):
	def __init__(self):
		super().__init__()
		self.left = 200
		self.top = 200
		self.width = 550
		self.height = 450
		self.initUI()


	def initUI(self):
		self.setWindowTitle('Chess')
		self.setGeometry(self.left, self.top, self.width, self.height)

		self.board = QtBoard(self)

		self.game = Game()

		self.show()

	def initGame_0(self):
		self.board = Board()
		self.human = Player('white')
		self.comp = Computer('black', self.board)
		self.history = []
		self.over = False




if __name__ == '__main__':

# just board
	# app = QApplication(sys.argv)
	# mainWidget = QtBoard()
	# mainWidget.show()
	# sys.exit(app.exec_())
# ----------------------------------------

	app = QApplication(sys.argv)
	mainWidget = QWidget()
	horizontalLayout = QHBoxLayout()
	board = QtBoard(mainWidget)
	horizontalLayout.addWidget(board)

	verticalLayout = QVBoxLayout()
	save_ses_btn = QPushButton('save', mainWidget)
	save_ses_btn.clicked.connect(board.save_session)
	verticalLayout.addWidget(save_ses_btn)
	load_ses_btn = QPushButton('load', mainWidget)
	load_ses_btn.clicked.connect(board.load_session)
	verticalLayout.addWidget(load_ses_btn)

	horizontalLayout.addLayout(verticalLayout)

	mainWidget.setLayout(horizontalLayout)
	mainWidget.show()
	sys.exit(app.exec_())



# ---
# qtgame - main app, иниц-ся доска, опции игры, история (гуи элементы) и сама логика игры

