import sys
import time
# from datetime import datetime
#

from PyQt5.QtCore import (QByteArray, QDataStream, QIODevice, QMimeData,
		QPoint, Qt, QObject, QPointF, QPropertyAnimation, pyqtProperty,
		QParallelAnimationGroup, QSequentialAnimationGroup)
from PyQt5.QtGui import QColor, QDrag, QPainter, QPixmap, QPainterPath
from PyQt5.QtWidgets import (QMainWindow, QApplication, QFrame, QHBoxLayout,
	QVBoxLayout, QLabel, QMessageBox, QPushButton, QWidget)



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


	def set_piece(self, piece_name, piece_color):
		self.del_piece()
		self.piece = QtPiece(piece_name, piece_color, self)
		# self.piece.show() # вызывается при создании фигуры

	def del_piece(self):
		if self.piece:
			self.piece.hide()
		self.piece = None


	def setColor(self):
		if self.id[0] in 'aceg' and self.id[1] in '1357'\
			or self.id[0] in 'bdfh' and self.id[1] in '2468':
			self.setStyleSheet('background-color:black;')
			self.color = 'black'
		else:
			self.setStyleSheet('background-color:white;')
			self.color = 'white'


	def dragEnterEvent(self, event):
		if event.source() == self:
			event.accept()
		else:
			# наведение на дугие клетки
			# здесь можно высчитывать возможность хода
			# либо для каждой кл заново, либо сразу сост спсок возм-ых и искать кл в этом списке
			event.acceptProposedAction()

	def dropEvent(self, event):
		from_pos = event.source().id
		to_pos = self.id
		self.board.make_human_move(from_pos, to_pos)

		# перемещение иконки
		event.setDropAction(Qt.MoveAction)
		event.accept()

		# if event.source() == self:
		#     pass


	def mousePressEvent(self, event):
		# if self.parent().moved_piece: # анимация пропадает, фигура копируется из анимации
		# 	self.parent().moved_piece.hide()
		# 	to_cell = self.parent().moved_piece.to_cell # вернуть эти две строчки, если надумаешь убрать update (put_pieces)
		# 	to_cell.piece = QtPiece(self.parent().moved_piece.name, self.parent().moved_piece.color, to_cell)
		# 	self.parent().moved_piece = None
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
		tempPixmap = QPixmap(pixmap)
		painter = QPainter()
		painter.begin(tempPixmap)
		painter.fillRect(pixmap.rect(), QColor(127, 127, 127, 127))
		painter.end()

		child.setPixmap(tempPixmap)

		if drag.exec_(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction) == Qt.MoveAction:
			# если перемещение в доступное место
			child.close()
		else:
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

		self.moved_piece = None
		# для custeling:
		self.moved_king = None
		self.moved_rook = None
		self.put_pieces()


	def print_all_cells00(self):
		for row in self.layout().children():
			for cell in [row.itemAt(i).widget() for i in range(8)]:
				piece = cell.piece.name if cell.piece else ""
				print(cell.id, piece) 


	def put_pieces(self):
		# ставит фигуры в соответствие со своей логической доской
		for row in self.layout().children():
			for cell in [row.itemAt(i).widget() for i in range(8)]:
				logic_piece = self.game.board[cell.id]
				if logic_piece:
					cell.set_piece(type(logic_piece).__name__, logic_piece.color)
				else:
					cell.del_piece()


	def need_to_promote_pawn00_работает(self, to_pos):
		if to_pos[1] != '1' and to_pos[1] != '8':
			return False
		logic_piece = self.game.board[to_pos]
		# if isinstance(logic_piece, Pawn): # так было когда logic promotion вызывался только через gui, сейчас он работает сам
		if isinstance(logic_piece, Queen):
			return True
		return False

	def promote_pawn00_работает(self, to_pos):
		if not self.need_to_promote_pawn(to_pos):
			raise MoveError()
			# return
		logic_pawn = self.game.board[to_pos]
		self.game.board[to_pos] = Queen(logic_pawn.color)
		qt_cell = self.get_cell(to_pos)
		qt_cell.set_piece('Queen', logic_pawn.color)

	def promote_comp_pawn00(self, to_pos):
		# invalid promotion
		# чтобы внешне ферзя не появлялось, но логически фигура ходила как ферзь
		if not self.need_to_promote_pawn(to_pos):
			raise MoveError()
			# return
		logic_pawn = self.game.board[to_pos]
		self.game.board[to_pos] = Queen(logic_pawn.color)


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
		from_pos, to_pos = self.game.comp.get_move()
		self.game.make_move(from_pos, to_pos)
		self.animate_move(from_pos, to_pos)

		from_cell = self.get_cell(from_pos)
		to_cell = self.get_cell(to_pos)

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
		# баг
		return from_pos == 'e1' and to_pos in ['a1', 'h1']

	def animate_custeling(self, from_pos, to_pos):
		if not self.is_custeling(from_pos, to_pos):
			raise Exception()
		# _1 так как рокировка пока только у человека
		rook_future_place = 'f1' if to_pos == 'h1' else 'd1'
		king_future_place = 'g1' if to_pos == 'h1' else 'c1'

		# необходимо чтобы скрывать его в mouse_press
		# иначе при наведении нельзя поставить фигуру на нее
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
		self.rook_anim.setDuration(1000) # speed
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


	def mousePressEvent(self, event):
		print('boooard')
		self.game.print_board()
		self.update()


	def load_session(self):
		self.game.load_session()
		self.put_pieces()

	def save_session(self):
		self.game.save_session('ses.txt')





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
