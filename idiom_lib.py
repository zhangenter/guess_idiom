# -*- coding=utf-8 -*-
import sys
import random
reload(sys)
sys.setdefaultencoding('utf-8')

class IdiomInfo(object):
	def __init__(self,idiom):
		self.idiom = idiom
		self.dire = 0
		self.word_arr = []

	def to_str(self):
		arr = []
		for word_info in self.word_arr:
			arr.append('%s %s %s'%(word_info.i,word_info.j,word_info.word))
		return '%s,%s,%s'%(self.idiom, self.dire, '|'.join(arr))

class WordInfo(object):
	def __init__(self, word, i, j):
		self.i = i
		self.j = j
		self.word = word
		self.is_lock = True
		self.state = -1
		self.hide_index = -1
		self.op_hide_index = -1

class Matrix(object):
    rows = 0
    cols = 0
    data = []

    def __init__(self, rows, cols, data=None):
        self.rows = rows
        self.cols = cols
        if data is None: data = [None for i in range(rows * cols)]
        self.data = data

    def set_val(self, x, y, val):
        self.data[y * self.cols + x] = val

    def get_val(self, x, y):
        return self.data[y * self.cols + x]

    def exist_val_four_around(self, x, y, ignore_set):
    	move_arr = [(-1,0),(1,0),(0,-1),(0,1)]

    	for dx,dy in move_arr:
    		tx = x + dx
    		ty = y + dy
    		if (tx,ty) in ignore_set: continue
    		if tx < 0 or tx >= self.cols or ty <0 or ty >= self.rows: continue
    		if self.data[ty * self.cols + tx]: return True
    	return False

class IdiomLib():
	def __init__(self, block_num=12):
		self.word_dic={}
		self.word_arr=[]
		self.block_num=block_num
		self.matrix = Matrix(self.block_num, self.block_num)
		self.idiom_dic={}
		self.all_word_num=0
		self.hide_arr = []

	def load_idiom_from_file(self, filename='words.txt'):
		f = open(filename)
		all_idiom = f.readlines()
		f.close()

		for idiom in all_idiom:
			idiom = idiom.strip().decode('utf-8')
			for word in idiom:
				if word not in self.word_dic: 
					self.word_dic[word] = [idiom]
				else:
				    self.word_dic[word].append(idiom)

		self.word_arr = list(self.word_dic.keys())

	def check_new_idiom(self, new_idiom, new_dire, word_info):
		windex = new_idiom.index(word_info.word)
		cx,cy = word_info.i, word_info.j
		ignore_set = set([(cx,cy)])

		new_idiom_word_arr=[]
		for i in range(-windex,-windex+len(new_idiom)): 
			if i==0: 
				new_idiom_word_arr.append(word_info)
			else:
				tx = cx+i  if new_dire == 0 else  cx
				if tx < 0 or tx >= self.block_num: return None,None

				ty = cy if new_dire == 0 else cy+i
				if ty < 0 or ty >= self.block_num: return None,None

				if self.matrix.exist_val_four_around(tx, ty, ignore_set): return None,None

				old_word_info = self.matrix.get_val(tx, ty)
				if old_word_info:
					return None,None

				new_word_info = WordInfo(new_idiom[i+windex], tx, ty)
				new_idiom_word_arr.append(new_word_info)


		return new_idiom_word_arr,windex

	def add_idiom_to_matrix(self, idiom_num):
		if idiom_num == 0: return 0
		for idiom,idiom_info in self.idiom_dic.items():
			dire = idiom_info.dire
			new_dire = 1 - dire
			for word_info in idiom_info.word_arr:
				word = word_info.word
				idiom_list = self.word_dic[word]
				for new_idiom in idiom_list:
					if new_idiom in self.idiom_dic: continue
					new_idiom_word_arr,windex = self.check_new_idiom(new_idiom, new_dire, word_info)
					if new_idiom_word_arr:
						new_idiom_info = IdiomInfo(new_idiom)
						new_idiom_info.dire = new_dire
						for new_index in range(len(new_idiom_word_arr)):
							new_word_info = new_idiom_word_arr[new_index]
							if new_index == windex:
								new_idiom_info.word_arr.append(word_info)
							else:
								self.matrix.set_val(new_word_info.i, new_word_info.j , new_word_info)
								new_idiom_info.word_arr.append(new_word_info)
						self.idiom_dic[new_idiom] = new_idiom_info

						return len(new_idiom) -1 + self.add_idiom_to_matrix(idiom_num - 1)

		return 0

	def get_idiom_matrix(self, idiom_num):
		self.idiom_dic={}
		cx = self.block_num/2-1
		cy = self.block_num/2-1
		n = random.randint(0,len(self.word_arr)-1)
		word = self.word_arr[n]
		idiom = self.word_dic[word][0]
		
		self.idiom_dic[idiom] = IdiomInfo(idiom)
		wn = len(idiom)
		last_i = -100
		for i in range(len(idiom)):
			word_info = WordInfo(idiom[i],cx-1+i,cy)
			self.matrix.set_val(cx-1+i,cy,word_info)
			self.idiom_dic[idiom].word_arr.append(word_info)

		wn += self.add_idiom_to_matrix(idiom_num-1)
		return wn

	def get_hide_arr(self, percent):
		self.hide_arr=[]
		for k,v in self.idiom_dic.items():
			n = random.randint(0, len(v.word_arr)-1)
			word_info = v.word_arr[n]
			if word_info.hide_index != -1:continue
			word = word_info.word
			info = self.matrix.get_val(word_info.i,word_info.j)
			info.word = ''
			info.hide_index = len(self.hide_arr)
			info.is_lock = False
			self.hide_arr.append([word_info.i,word_info.j,word,None])

		tmp_arr = []
		for i in range(self.block_num):
			for j in range(self.block_num):
				info = self.matrix.get_val(i,j)
				if info and info.word:
					tmp_arr.append((i,j,info.word))

		while len(self.hide_arr) < self.all_word_num*percent:
			n = random.randint(0,len(tmp_arr)-1)
			i,j,word = tmp_arr.pop(n)
			info = self.matrix.get_val(i,j)
			info.word = ''
			info.hide_index = len(self.hide_arr)
			info.is_lock = False
			self.hide_arr.append([i,j,word,None])

		return self.hide_arr  

	def get_next_select(self, x, y):
		arr = []
		for i in range(self.block_num):
			for j in range(self.block_num):
				info = self.matrix.get_val(i, j)
				if info is not None and len(info.word) == 0:
					dist = (i-x)*(i-x)+(j-y)*(j-y)
					if i<x: dist+=0.2
					if j<y: dist+=0.4
					arr.append((i,j,dist))
		if len(arr) == 0:
			return None
		arr.sort(cmp=lambda x,y:cmp(x[-1],y[-1]))
		return (arr[0][0],arr[0][1])

	def check_idiom(self):
		for idiom, idiom_info in self.idiom_dic.items():
			tmp_idiom_str = ''
			word_arr = idiom_info.word_arr
			for word_info in word_arr:
				word = word_info.word
				if len(word) > 0:
					tmp_idiom_str+=word
			if len(tmp_idiom_str) == len(idiom):
				state = 1 if tmp_idiom_str == idiom else 2
			else:
				state = 0

			for word_info in word_arr:
				if word_info.state != 1: word_info.state = state

		for idiom, idiom_info in self.idiom_dic.items():
			word_arr = idiom_info.word_arr
			for word_info in word_arr:
				if word_info.state != 1:
					return False
		return True

	stage = 1

	def init(self, new_stage):
		idiom_num = (new_stage/5)+3
		if new_stage>100:
			percent = 0.7
		else:
			percent = 0.2+(new_stage*1.0/100)*(0.7-0.2)
		self.matrix = Matrix(self.block_num, self.block_num)
		self.all_word_num = self.get_idiom_matrix(idiom_num)
		self.get_hide_arr(percent)
		self.select_rect = self.hide_arr[0][0],self.hide_arr[0][1]

if __name__ == '__main__':
	lib = IdiomLib()
	lib.load_idiom_from_file()

	arr = []
	for i in range(1,101):
		lib.init(i)
		idiom_arr = []
		for k,v in lib.idiom_dic.items():
			idiom_arr.append(v.to_str())
		hide_arr = []
		for x,y,word,op in lib.hide_arr:
			hide_arr.append('%s %s %s'%(x,y,word))
		arr.append({'word_num':lib.all_word_num,'idiom_arr':';'.join(idiom_arr),'hide_arr':';'.join(hide_arr)})
	arr.sort(cmp=lambda x,y:cmp(x['word_num'], y['word_num']))

	import json
	f = open('idiom.json','w+') 
	f.write(json.dumps(arr))
	f.close()

