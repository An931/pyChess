# from pickle import dump, load
import pickle

class Saver:
	def save_session(name, game_obj):
		filename = 'sessions\{}.pickle'.format(name)
		with open (filename, 'wb') as f:
			pickle.dump(game_obj, f)

	def load_session(name):
		filename = 'sessions\{}.pickle'.format(name)
		with open (filename, 'rb') as f:
			game = pickle.load(f)
		return game

class P:
	def __init__(self):
		self.p = 'a'
		self.a='v'
		print(self.p, self.a)


if __name__ == '__main__':
	p = P()
	Saver.save_session('h', p)
	Saver.load_session()