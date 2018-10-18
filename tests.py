import unittest
from pieces import *
from board import *
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


class TestBoardMethods(unittest.TestCase):
    def test_get_pathway_cells(self):
        cells = Board.get_pathway_cells('b2', 'b5')
        self.assertEqual(cells, ['b3', 'b4'])
        cells = Board.get_pathway_cells('b2', 'e2')
        self.assertEqual(cells, ['c2', 'd2'])
        cells = Board.get_pathway_cells('b2', 'e5')
        self.assertEqual(cells, ['c3', 'd4'])
        cells = Board.get_pathway_cells('b2', 'c4')
        self.assertEqual(cells, [])

    def test_is_barrier_on_pathway(self):
        b = Board()
        for p in 'a1 b1 c1 d1 e1 f1 g1 h1'.split():
            to = p[0]+str(int(p[1])+2)
            self.assertTrue(b.is_barrier_on_pathway(p, to))
        for p in 'a2 b2 c2 d2 e2 f2 g2 h2'.split():
            to = p[0]+str(int(p[1])+2)
            self.assertFalse(b.is_barrier_on_pathway(p, to))


    def test_evaluate_can_move(self):
        b = Board()
        p = Player('white')
        self.assertTrue(b.evaluate_can_move('a2', 'a4', p))
        self.assertTrue(b.evaluate_can_move('b1', 'c3', p))

        self.assertFalse(b.evaluate_can_move('a2', 'a5', p))
        self.assertFalse(b.evaluate_can_move('a1', 'a4', p))
        self.assertFalse(b.evaluate_can_move('b4', 'b5', p))


    def test_correct_movement(self):
        b = Board()
        p = Player('white')
        b.make_move('b1', 'c3', p)
        self.assertTrue(isinstance(b.board['b1'], Empty))
        self.assertTrue(isinstance(b.board['c3'], Knight))

    def test_correct_capture(self):
        b = Board()
        p = Player('white')
        b.board['b3'] = King('black')
        b.make_move('a2', 'b3', p)
        self.assertTrue(isinstance(b.board['a2'], Empty))
        self.assertTrue(isinstance(b.board['b3'], Pawn))
        self.assertTrue(isinstance(b.captured_pieces[1], King))

    def test_incorrect_capture(self):
        b = Board()
        p = Player('white')
        b.board['b3'] = King('white')
        board = dict(b.board)
        b.make_move('a2', 'b3', p)
        self.assertEqual(board, b.board)


    def test_empty_movement(self):
        b = Board()
        board = dict(b.board)
        p = Player('white')
        b.make_move('d5', 'c3', p)
        self.assertEqual(board, b.board)


    def test_incorrect_piece_movement(self):
        b = Board()
        board = dict(b.board)
        p = Player('white')
        b.make_move('a2', 'b3', p)
        self.assertEqual(board, b.board)


class TestComputerAI(unittest.TestCase):
    def test_movments_of_piece(self):
      b = Board()
      c = Computer('black', b)
      pawn_m = c.get_movments_of_piece('a7')
      self.assertEqual(set(pawn_m), set(['a6', 'a5']))

    def test_get_all_movements(self):
      b = Board()
      c = Computer('black', b)
      moves_from = c.get_all_movements()
      self.assertEqual(len(moves_from), 10)
      moves_to = []
      for k in moves_from.keys():
      	moves_to += moves_from[k]
      self.assertEqual(len(moves_to), 20)

    def test_sorted_movements(self):
      b = Board()
      c = Computer('black', b)
      b.board['d3'] = Knight('black')
      moves = c.get_sorted_movements()
      self.assertEqual(moves[0], ('d3', 'e1'))
      self.assertEqual(moves[1], ('d3', 'c1'))

    def test_make_move(self):
      b = Board()
      c = Computer('black', b)
      b.board['c6'] = Queen('white')
      b.board['e6'] = Bishop('white')
      move = c.make_move()
      self.assertEqual(move[1], 'c6')


class TestGameMethods(unittest.TestCase):
    def test_extract_hum_move(self):
      g = Game()
      self.assertIsNone(g.extract_hum_move('wrong'))
      self.assertIsNone(g.extract_hum_move('sm wg'))
      self.assertEqual(g.extract_hum_move('a2 a4'), ('a2', 'a4'))
      
    def test_evaluate_is_finished(self):
      g = Game()
      self.assertFalse(g.evaluate_is_finished())
      g.board.board['d7'] = Pawn('white', 'up')
      g.next_move('d7 e8')
      self.assertTrue(g.evaluate_is_finished())
      self.assertTrue(g.over)
      self.assertTrue(isinstance(g.winner, Player))

    def test_next_move(self):
      g = Game()
      g.next_move('b1 c3')
      self.assertTrue(isinstance(g.board.board['c3'], Knight))
      self.assertEqual(g.history[len(g.history) - 2], ('b1', 'c3'))


if __name__ == '__main__':
    unittest.main()