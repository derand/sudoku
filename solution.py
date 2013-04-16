#!/usr/bin/env python
# -*- coding: utf-8 -*-


__version__ = '0.1'
__author__ = 'Andrey Derevyagin'
__copyright__ = 'Copyright © 2013, Andrey Derevyagin'


import math
from sets import Set
import sys


class Node(object):
	def __init__(self, data):
		self.data = data
		self.children = []
		self.parent = None
		self.depth = 0

	def add_child(self, obj):
		obj.parent = self
		obj.depth = self.depth + 1
		self.children.append(obj)

	def __str__(self):
		rv = ''
		for row in self.data:
			row_str = ''
			for el in row:
				if isinstance(el, int):
					row_str += ' %x'%el
				elif isinstance(el, Set) and len(el)==1:
					row_str += ' %x'%list(el)[0]
				else:
					row_str += ' -'
					#row_str += ' %s'%list(el)
			rv += '%s\n'%row_str[1:]
		return rv.strip()


class Sudoku(object):
	def __init__(self, initial):
		super(Sudoku, self).__init__()
		self.__length = len(initial)
		self.__piece = int(math.sqrt(self.__length))
		for row in range(len(initial)):
			if len(initial[row]) != self.__length:
				raise ValueError('Length error at row %d (should by %d)'%(row, self.__length))
		self.preocess_tree = Node(self.set_posibles(initial))
		self.solution_event = None
		self.dead_end_event = None
		self.solution_counter = 0
		self.dead_end_counter = 0
		#self.test()

	def col(self, data, col):
		rv = []
		for row in range(len(data)):
			rv.append(data[row][col])
		return tuple(rv)

	def row(self, data, row):
		return tuple(data[row])

	def square(self, data, num):
		rv = []
		__row = int(num / self.__piece) * self.__piece
		__col = int(num % self.__piece) * self.__piece
		for row in range(self.__piece):
			for col in range(self.__piece):
				rv.append(data[__row+row][__col+col])
		return rv

	'''
	def __point_check(self, funct, dt, prm, val):
		rm = False
		for el in funct(dt, prm):
			if type(el) is int:
				if el in val:
					val.remove(el)
					rm = True
			if (type(el)==type(Set()) and len(el)==1):
				if list(el)[0] in val:
					val.remove(list(el)[0])
					rm = True
		return rm
	'''

	def __array_check(self, arr):
		changed = False
		#positions = [Set()]*self.__length
		positions = []
		for i in range(self.__length): positions.append(Set())
		for i in range(len(arr)):
			el = arr[i]
			#if len(el) > 1:
			for tmp in list(el):
				positions[tmp-1].add(i)
		for i in range(len(positions)):
			if len(positions[i])==1:
				val = arr[list(positions[i])[0]]
				for el in list(val):
					if el != i+1:
						val.remove(el)
						changed = True
		return changed

	def __array_dublicates_check(self, arr):
		changed = False
		for c in range(2, self.__length-1):
			tmp = filter(lambda el: len(el)==c, arr)
			for i in range(len(tmp)-1):
				k = 1
				for j in range(i+1, len(tmp)):
					if tmp[i]==tmp[j]: k += 1
				if k == c:
					for el in arr:
						if el != tmp[i]:
							for v in list(tmp[i]):
								if v in el:
									el.remove(v)
									changed = True
		return changed

	def __check(self, data):
		rm = False

		# delete used numberts from rows, colums and square
		for row in range(len(data)):
			for col in range(len(data[row])):
				if isinstance(data[row][col], Set) and len(data[row][col]) > 1:
					val = data[row][col]
					__col_arr = self.col(data, col)
					for i in range(len(__col_arr)):
						if i != row and len(__col_arr[i])==1 and list(__col_arr[i])[0] in val:
							val.remove(list(__col_arr[i])[0])
							rm = True
					__row_arr = self.row(data, row)
					for i in range(len(__row_arr)):
						if i != col and len(__row_arr[i])==1 and list(__row_arr[i])[0] in val:
							val.remove(list(__row_arr[i])[0])
							rm = True
					__square_arr = self.square(data, self.col_and_row_to_num(row, col))
					for i in range(len(__square_arr)):
						if i != (col%3 + (row%3)*3) and len(__square_arr[i])==1 and list(__square_arr[i])[0] in val:
							val.remove(list(__square_arr[i])[0])
							rm = True
					#rm |= self.__point_check(self.col, data, col, val)
					#rm |= self.__point_check(self.row, data, row, val)
					#rm |= self.__point_check(self.square, data, self.col_and_row_to_num(row, col), val)
					data[row][col] = val

		# search dublicates (like 2/5 and 2/5 in one line)
		for i in range(self.__length):
			rm |= self.__array_dublicates_check(self.col(data, i))
			rm |= self.__array_dublicates_check(self.row(data, i))
			rm |= self.__array_dublicates_check(self.square(data, i))

		# search single numbers variants at rows, colums and squares
		for i in range(self.__length):
			rm |= self.__array_check(self.col(data, i))
			rm |= self.__array_check(self.row(data, i))
			rm |= self.__array_check(self.square(data, i))
		return rm

	def __is_finish(self, data):
		is_finish = 1
		for row in data:
			for col in row:
				if len(col)==0:
					return -1
				elif len(col)!=1:
					is_finish = 0
		return is_finish

	def __select_idx(self, data):
		__row = -1
		__col = -1
		__len = self.__length
		for row in range(len(data)):
			for col in range(len(data[row])):
				if len(data[row][col]) > 1 and len(data[row][col]) < __len:
					__row = row
					__col = col
					__len = len(data[row][col])
		return (__row, __col, __len)

	def __copy(self, data):
		rv = []
		for row in data:
			new_row = []
			for col in row:
				new_row.append(Set(list(col)))
			rv.append(new_row)
		return tuple(rv)

	def __search(self, tree):
		while True:
			if not self.__check(tree.data):
				break
		status = self.__is_finish(tree.data)
		if status > 0:
			self.solution_counter += 1 
			if self.solution_event != None:
				self.solution_event(self, tree)
			#print tree
			#print
		elif status == 0:
			position = self.__select_idx(tree.data)
			if position[0] < 0 or position[1] < 0:
				raise ValueError('Best fork position search error (%d, %d):\n%s'%(position[0], position[1], tree.__str__()))
			for v in list(tree.data[position[0]][position[1]]):
				tmp = self.__copy(tree.data)
				tmp[position[0]][position[1]] = Set([v])
				tree.add_child(Node(tmp))
			for srch in tree.children:
				self.__search(srch)
		elif status < 0:
			self.dead_end_counter += 1
			if self.dead_end_event != None:
				self.dead_end_counter(self, tree)


	def search(self):
		return self.__search(self.preocess_tree)

	def col_and_row_to_num(self, row, col):
		return col / self.__piece + int(row / self.__piece) * self.__piece

	def set_posibles(self, data):
		rv = []
		for row in range(len(data)):
			new_row = []
			for col in range(len(data[row])):
				val = None
				if not isinstance(data[row][col], int):
					val = Set(range(1, self.__length+1))
					#self.__point_check(self.col, data, col, val)
					#self.__point_check(self.row, data, row, val)
					#self.__point_check(self.square, data, self.col_and_row_to_num(row, col), val)
				else:
					val = Set([data[row][col]])
				new_row.append(val)
			rv.append(new_row)
		return tuple(rv)

	def test(self):
		x = (Set([9]), Set([4]), Set([2,3,5]), Set([1]), Set([8]), Set([7]), Set([2,3,5]), Set([2,3,5]), Set([2,3]))
		x = []
		for row in range(9):
			y = []
			for col in range(9):
				y.append(Set([col%3 + (row%3)*3]))
			x.append(y)
		print Node(x)


	def __str__(self):
		return self.preocess_tree.__str__()



if __name__=='__main__':
	data01 = (
		('', '', '',  1,  8,  7, '', '', ''),
		('', '',  3, '', '', '', '', '', ''),
		('', '', '', '', '',  2, '', '',  4),
		('', '', '', '', '', '',  3,  2, ''),
		( 8, '', '', '',  5, '', '', '', ''),
		('',  1, '', '', '', '', '',  7, ''),
		('',  9, '',  3, '', '', '',  5, ''),
		('',  4,  5, '', '',  9,  2, '', ''),
		( 1, '', '', '', '',  8,  7, '', ''),
	)
	data02 = (
		( 9,  6,  4,  1,  8,  7, '', '', ''),
		('', '',  3, '', '', '', '', '', ''),
		('', '', '',  9, '',  2, '', '',  4),
		('', '', '', '', '', '',  3,  2, ''),
		( 8, '', '', '',  5, '', '', '', ''),
		('',  1, '', '', '', '', '',  7, ''),
		('',  9, '',  3, '', '', '',  5, ''),
		('',  4,  5, '', '',  9,  2, '', ''),
		( 1, '', '', '', '',  8,  7, '', ''),
	)
	data03 = (
		( 9,  6,  4,  1,  8,  7, '', '', ''),
		('',  8,  3, '', '', '', '', '', ''),
		('', '', '', '', '',  2, '', '',  4),
		('', '', '',  7, '', '',  3,  2, ''),
		( 8, '', '', '',  5, '', '', '', ''),
		('',  1, '', '', '',  3,  6,  7, ''),
		('',  9, '',  3, '', '', '',  5, ''),
		('',  4,  5, '', '',  9,  2, '', ''),
		( 1, '', '', '', '',  8,  7, '', ''),
	)
	data04 = (
		( 1, '', '', '', '', '', '', '', ''),
		('', '', '', '', '', '', '', '', ''),
		('', '', '', '', '', '', '', '', ''),
		('', '', '', '', '', '', '', '', ''),
		('', '', '', '', '', '', '', '', ''),
		('', '', '', '', '', '', '', '', ''),
		('', '', '', '', '', '', '', '', ''),
		('', '', '', '', '', '', '', '', ''),
		('', '', '', '', '', '', '', '', ''),
	)
	data05 = (
		('',  7, '', '',  5,  8, '', '', ''),
		('', '',  1,  9, '', '', '', '',  2),
		('',  5, '',  3, '', '', '',  6, ''),
		( 9, '', '', '', '',  3, '',  2, ''),
		('',  1, '', '',  2,  7,  6, '', ''),
		('', '', '', '', '', '',  1, '', ''),
		('', '', '', '', '',  9, '',  5,  1),
		('', '', '', '', '', '',  2,  9,  7),
		('', '', '', '', '',  5,  3, '', ''),
	)

	s = data05
	sudoku = Sudoku(s)
	print 'Sudoku:\n%s\n'%Node(s)
	sudoku.solution_event = lambda sender,tree: sys.stdout.write('Solution %d (depth %d):\n%s\n\n'%(sender.solution_counter, tree.depth, tree)) 
	sudoku.dead_end_event = None
	sudoku.search()
	print 'Solutions: %d, bad: %d'%(sudoku.solution_counter, sudoku.dead_end_counter)

