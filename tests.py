import unittest
from pieces import *
from players import *
from game import *


class TestPiecesMovements(unittest.TestCase):
		def test_rook_movement(self):
				piece = Rook('white')
				self.assertTrue(piece.can_move('a1', 'a5'))
				self.assertTrue(piece.can_move('a1', 'd1'))
				self.assertFalse(piece.can_move('a1', 'b2'))

		def test_knight_movement(self):
				piece = Knight('white')
				self.assertTrue(piece.can_move('b1', 'a3'))
				self.assertFalse(piece.can_move('b1', 'b2'))

		def test_bishop_movement(self):
				piece = Bishop('white')
				self.assertTrue(piece.can_move('c1', 'b2'))
				self.assertTrue(piece.can_move('c1', 'f4'))
				self.assertFalse(piece.can_move('c1', 'c3'))

		def test_queen_movement(self):
				piece = Queen('white')
				self.assertTrue(piece.can_move('d1', 'd5'))
				self.assertTrue(piece.can_move('d1', 'a1'))
				self.assertTrue(piece.can_move('d1', 'f3'))
				self.assertFalse(piece.can_move('d1', 'c3'))

		def test_king_movement(self):
				piece = King('white')
				self.assertTrue(piece.can_move('e1', 'e2'))
				self.assertTrue(piece.can_move('e1', 'd1'))
				self.assertTrue(piece.can_move('e1', 'f2'))
				self.assertFalse(piece.can_move('e1', 'e3'))

		def test_pawn_movement(self):
				piece = Pawn('white', 'up')
				self.assertTrue(piece.can_move('a2', 'a3'))
				self.assertTrue(piece.can_move('a2', 'a4'))
				self.assertFalse(piece.can_move('a2', 'a1'))
				self.assertFalse(piece.can_move('a3', 'a5'))
				self.assertFalse(piece.can_move('a2', 'b3'))

		def test_pawn_capture(self):
				piece = Pawn('white', 'up')
				self.assertTrue(piece.can_capture('a2', 'b3'))
				self.assertFalse(piece.can_capture('a3', 'b2'))
				self.assertFalse(piece.can_capture('a2', 'a3'))


class TestComputerAI(unittest.TestCase):
	def get_comp(self):
		g = LogicGame()
		c = Computer(g, 'black')
		return c

	def test_movments_of_piece(self):
		c = self.get_comp()
		pawn_m = c.game.get_movments_of_piece('a7')
		self.assertEqual(set(pawn_m), set(['a6', 'a5']))

	def test_get_all_movements(self):
		c = self.get_comp()
		moves_from = c.game.get_all_movements(c.color)
		self.assertEqual(len(moves_from), 10)
		moves_to = []
		for k in moves_from.keys():
			moves_to += moves_from[k]
		self.assertEqual(len(moves_to), 20)

	def test_sorted_movements(self):
		c = self.get_comp()
		c.game.board['d3'] = Knight('black')
		moves = c.game.get_sorted_movements(c.color)
		self.assertEqual(moves[0], ('d3', 'e1'))
		self.assertEqual(moves[1], ('d3', 'c1'))

	def test_make_move(self):
		c = self.get_comp()
		c.game.board['c6'] = Queen('white')
		c.game.board['e6'] = Bishop('white')
		move = c.get_move()
		self.assertEqual(move[1], 'c6')


class TestGameMethods(unittest.TestCase):
		def test_evaluate_is_finished(self):
			g = LogicGame()
			self.assertFalse(g.over)
			g.board['d7'] = Pawn('white', 'up')
			g.make_move('d7', 'e8')
			self.assertTrue(g.over)
			self.assertEqual(g.win_color, 'white')

		def test_next_move(self):
			g = LogicGame()
			g.make_move('b1', 'c3')
			self.assertTrue(isinstance(g.board['c3'], Knight))

		def test_pathway(self):
			g = LogicGame()
			self.assertEqual(g.get_pathway_cells('a1', 'a4'), ['a2', 'a3'])
			self.assertEqual(g.get_pathway_cells('a1', 'd1'), ['b1', 'c1'])
			self.assertEqual(g.get_pathway_cells('a1', 'd4'), ['b2', 'c3'])
			self.assertEqual(g.get_pathway_cells('d4', 'g1'), ['e3', 'f2'])
			self.assertEqual(g.get_pathway_cells('a1', 'b5'), [])

		def test_barrier_on_pathway(self):
			g = LogicGame()
			self.assertTrue(g.is_barrier_on_pathway('a1', 'c1'))
			self.assertFalse(g.is_barrier_on_pathway('a2', 'a4'))

		def test_custeling(self):
			g = LogicGame()
			g.board['f1'] = ""
			g.board['g1'] = ""
			g.make_move('e1', 'h1')
			self.assertTrue(isinstance(g.board['g1'], King))
			self.assertTrue(isinstance(g.board['f1'], Rook))

		def test_enpassant(self):
			g = LogicGame()
			g.board['d4'] = Pawn('black', 'down')
			g.make_move('c2', 'c4')
			g.make_move('d4', 'c3')
			self.assertTrue(isinstance(g.board['c3'], Pawn))
			self.assertEqual(g.board['c4'], '')

		def test_promotion(self):
			g = LogicGame()
			g.board['c7'] = Pawn('white', 'up')
			g.make_move('c7', 'b8')
			self.assertTrue(isinstance(g.board['b8'], Queen))

if __name__ == '__main__':
		unittest.main()