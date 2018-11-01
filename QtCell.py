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

class QtCell(QFrame):
	def __init__(self, id, qtgame, parent):
		super(QtCell, self).__init__(parent)
		# self.game = game
		self.piece = None
		self.id = id
		self.game = qtgame
		self.set_сolor()

		self.setToolTip('cell {}'.format(self.id))

		self.setMinimumSize(50, 50)
		self.setLineWidth(10)
		self.setAcceptDrops(True)

	def set_piece(self, piece_name, piece_color):
		self.del_piece()
		self.piece = QtPiece(piece_name, piece_color, self)

	def del_piece(self):
		if self.piece:
			self.piece.hide()
		self.piece = None

	def set_сolor(self):
		if self.id[0] in 'aceg' and self.id[1] in '1357'\
			or self.id[0] in 'bdfh' and self.id[1] in '2468':
			self.setStyleSheet('background-color:black;')
			self.color = 'black'
		else:
			self.setStyleSheet('background-color:white;')
			self.color = 'white'

	def highlight(self, do=True):
		if do:
			color = 'red'
			self.setStyleSheet('border: 2px solid {}; background-color:{};'.format(color, self.color))
		else:
			self.setStyleSheet('background-color:{};'.format(self.color))
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
		self.game.try_make_move(from_pos, to_pos)


	def mousePressEvent(self, event):
		# нажатие именно на фигуру
		child = self.childAt(event.pos())
		if not child:
			return
		if child.color != self.game.acting_player.color:
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


class QtPiece(QLabel):
	def __init__(self, name, color, parent):
		pixmap = QPixmap('pieces_img/{}.png'.format(color[0]+'_'+name))
		pixmap = pixmap.scaled(50, 50)
		super(QLabel, self).__init__(parent)
		self.setPixmap(pixmap)
		self.setMinimumSize(50, 50)

		self.setToolTip(color + ' ' + name)

		self.name = name
		self.color = color
		self.cell = parent
		self.show()


