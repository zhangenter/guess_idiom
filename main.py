# -*- coding=utf-8 -*-
import sys
import random
import pygame
from pygame.locals import *
reload(sys)
sys.setdefaultencoding('utf-8')

f = open('words.txt')
all_idiom = f.readlines()
f.close()

word_dic = {}
for idiom in all_idiom:
	idiom = idiom.strip().decode('utf-8')
	for word in idiom:
		if word not in word_dic: 
			word_dic[word] = [idiom]
		else:
		    word_dic[word].append(idiom)

word_arr = list(word_dic.keys())

header_height = 30
main_space = 20

block_size = 36
block_num=12
bspace = 2
space = 20
width = block_size * block_num + main_space * 2
height = header_height + block_size * block_num + main_space * 2 + (block_size+space) * 3

pygame.init()
screen = pygame.display.set_mode((width,height))
screencaption = pygame.display.set_caption(u'成语填空')

font = pygame.font.Font(u'syht.otf', int(block_size*0.8))

dray_gray = 50,50,50
white = 255,255,255
#textImage = font.render(u'你好', True, white)

class IdiomInfo(object):
	def __init__(self,idiom):
		self.idiom = idiom
		self.dire = 0
		self.word_arr = []

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

def check_new_idiom(matrix, new_idiom, new_dire, word_info):
	windex = new_idiom.index(word_info.word)
	cx,cy = word_info.i, word_info.j
	ignore_set = set([(cx,cy)])

	new_idiom_word_arr=[]
	for i in range(-windex,-windex+len(new_idiom)): 
		if i==0: 
			new_idiom_word_arr.append(word_info)
		else:
			tx = cx+i  if new_dire == 0 else  cx
			if tx < 0 or tx >= block_num: return None,None

			ty = cy if new_dire == 0 else cy+i
			if ty < 0 or ty >= block_num: return None,None

			if matrix.exist_val_four_around(tx, ty, ignore_set): return None,None

			old_word_info = matrix.get_val(tx, ty)
			if old_word_info:
				return None,None

			new_word_info = WordInfo(new_idiom[i+windex], tx, ty)
			new_idiom_word_arr.append(new_word_info)


	return new_idiom_word_arr,windex

def add_idiom_to_matrix(matrix, word_dic, idiom_dic, idiom_num):
	if idiom_num == 0: return 0
	for idiom,idiom_info in idiom_dic.items():
		dire = idiom_info.dire
		new_dire = 1 - dire
		for word_info in idiom_info.word_arr:
			word = word_info.word
			idiom_list = word_dic[word]
			for new_idiom in idiom_list:
				if new_idiom in idiom_dic: continue
				new_idiom_word_arr,windex = check_new_idiom(matrix, new_idiom, new_dire, word_info)
				if new_idiom_word_arr:
					new_idiom_info = IdiomInfo(new_idiom)
					new_idiom_info.dire = new_dire
					for new_index in range(len(new_idiom_word_arr)):
						new_word_info = new_idiom_word_arr[new_index]
						if new_index == windex:
							new_idiom_info.word_arr.append(word_info)
						else:
							matrix.set_val(new_word_info.i, new_word_info.j , new_word_info)
							new_idiom_info.word_arr.append(new_word_info)
					idiom_dic[new_idiom] = new_idiom_info

					return len(new_idiom) -1 + add_idiom_to_matrix(matrix, word_dic, idiom_dic, idiom_num - 1)

	return 0

def get_idiom_matrix(word_arr, word_dic, idiom_num):
	cx = 4
	cy = 4
	matrix = Matrix(block_num, block_num)
	n = random.randint(0,len(word_arr)-1)
	word = word_arr[n]
	idiom = word_dic[word][0]
	idiom_dic={}
	idiom_dic[idiom] = IdiomInfo(idiom)
	wn = len(idiom)
	last_i = -100
	for i in range(len(idiom)):
		word_info = WordInfo(idiom[i],cx-1+i,cy)
		matrix.set_val(cx-1+i,cy,word_info)
		idiom_dic[idiom].word_arr.append(word_info)

	wn += add_idiom_to_matrix(matrix, word_dic, idiom_dic, idiom_num-1)
	return matrix, idiom_dic, wn


bg_image = pygame.image.load('bg.jpeg')
bg_image = pygame.transform.scale(bg_image,(width, height))

bg2_image = pygame.image.load('bg2.jpeg')
bg2_image = pygame.transform.scale(bg2_image,(block_size*block_num,block_size*block_num))

block_bg_image = pygame.image.load('tzg.jpg')
block_bg_image = pygame.transform.scale(block_bg_image,(block_size-bspace*2,block_size-bspace*2))

def get_hide_arr(matrix, idiom_dic, all_word_num, percent):
	hide_arr = []
	for k,v in idiom_dic.items():
		n = random.randint(0, len(v.word_arr)-1)
		word_info = v.word_arr[n]
		if word_info.hide_index != -1:continue
		word = word_info.word
		info = matrix.get_val(word_info.i,word_info.j)
		info.word = ''
		info.hide_index = len(hide_arr)
		info.is_lock = False
		hide_arr.append([word_info.i,word_info.j,word,None])

	tmp_arr = []
	for i in range(block_num):
		for j in range(block_num):
			info = matrix.get_val(i,j)
			if info and info.word:
				tmp_arr.append((i,j,info.word))

	while len(hide_arr) < all_word_num*percent:
		n = random.randint(0,len(tmp_arr)-1)
		i,j,word = tmp_arr.pop(n)
		info = matrix.get_val(i,j)
		info.word = ''
		info.hide_index = len(hide_arr)
		info.is_lock = False
		hide_arr.append([i,j,word,None])

	return hide_arr  

def get_next_select(matrix, x, y):
	arr = []
	for i in range(block_num):
		for j in range(block_num):
			info = matrix.get_val(i, j)
			if info is not None and len(info.word) == 0:
				dist = (i-x)*(i-x)+(j-y)*(j-y)
				if i<x: dist+=0.2
				if j<y: dist+=0.4
				arr.append((i,j,dist))
	if len(arr) == 0:
		return None
	arr.sort(cmp=lambda x,y:cmp(x[-1],y[-1]))
	return (arr[0][0],arr[0][1])

def check_idiom():
	for idiom, idiom_info in idiom_dic.items():
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

	for idiom, idiom_info in idiom_dic.items():
		word_arr = idiom_info.word_arr
		for word_info in word_arr:
			if word_info.state != 1:
				return False
	return True

stage = 1

def init(new_stage):
	idiom_num = (new_stage/5)+3
	if new_stage>100:
		percent = 0.7
	else:
		percent = 0.2+(new_stage*1.0/100)*(0.7-0.2)
	matrix,idiom_dic,all_word_num = get_idiom_matrix(word_arr, word_dic, idiom_num)
	hide_arr = get_hide_arr(matrix, idiom_dic, all_word_num, percent)
	select_rect = hide_arr[0][0],hide_arr[0][1]
	stage_textImage = pygame.font.Font(u'syht.otf', 30).render(u'第%s关'%new_stage, True, dray_gray)
	return matrix,idiom_dic,all_word_num,hide_arr,select_rect,stage_textImage

matrix,idiom_dic,all_word_num,hide_arr,select_rect,stage_textImage = init(stage)

stage_font_width, stage_font_height = stage_textImage.get_size()
stage_x = (width - stage_font_width)/2
stage_y = (header_height - stage_font_height)/2+main_space/2
while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
		   	pygame.quit()
		   	exit()

		if event.type == MOUSEBUTTONDOWN:
			pressed_array = pygame.mouse.get_pressed()
			if pressed_array[0]:
				x, y = pygame.mouse.get_pos()

				for i in range(block_num):
					for j in range(block_num):
						bx = main_space + block_size*i+bspace
						by = header_height + main_space + block_size*j+bspace
						if x >= bx and x <= bx+block_size-bspace*2 and y >= by and y<= by+block_size-bspace*2:
							info = matrix.get_val(i, j)
							if info and info.state != 1 and info.hide_index >= 0:
								if info.op_hide_index>=0:
									hide_arr[info.op_hide_index][-1] = None
									info.word = ''
									info.op_hide_index=-1
									check_idiom()
								select_rect = i,j
								break

				sx = main_space
				sy = header_height + main_space+ block_size*block_num +space
				n = 0
				for hi in range(len(hide_arr)):
					tmp_x = sx + (n%block_num)*block_size
					tmp_y = sy + (n/block_num)*block_size
					if hide_arr[hi][-1] is None and x >= tmp_x and x <= tmp_x+block_size-bspace*2 and y >= tmp_y and y<= tmp_y+block_size-bspace*2:
						info = matrix.get_val(select_rect[0],select_rect[1])
						info.word = hide_arr[hi][2]
						info.op_hide_index = hi
						info.state = 0
						hide_arr[hi][-1] = select_rect
						new_select_rect = get_next_select(matrix, select_rect[0],select_rect[1])
						select_rect = new_select_rect
						flag = check_idiom()
						if flag:
							stage += 1
							matrix,idiom_dic,all_word_num,hide_arr,select_rect,stage_textImage = init(stage)
						break

					n += 1


	screen.blit(bg_image, (0,0))
	screen.blit(stage_textImage, (stage_x,stage_y))

	panel = screen.subsurface((main_space,header_height+main_space,block_size*block_num,block_size*block_num))
	panel.blit(bg2_image, (0,0))

	for i in range(block_num):
		for j in range(block_num):
			info = matrix.get_val(i,j)
			if info is not None:
				bx = block_size*i+bspace
				by = block_size*j+bspace
				panel.blit(block_bg_image, (bx,by))
				
				if info.state == 1:
					textImage = font.render(info.word, True, (30,144,30))
				elif info.state == 2:
					textImage = font.render(info.word, True, (255,0,0))
				elif info.is_lock == 1:
					textImage = font.render(info.word, True, (150,150,150))
				else:
					textImage = font.render(info.word, True, dray_gray)

				tw, th = textImage.get_size()
				dx=(block_size-bspace*2-tw)/2
				dy=(block_size-bspace*2-th)/2
				panel.blit(textImage, (bx+dx,by+dy))
				if (i,j) == select_rect:
					pygame.draw.rect(panel,(255,0,0),(bx,by,block_size-bspace*2,block_size-bspace*2),2)

	sx = main_space
	sy = header_height + main_space+ block_size*block_num +space
	n = 0
	for i,j,word,op in hide_arr:
		screen.blit(block_bg_image, (sx + (n%block_num)*block_size,sy + (n/block_num)*block_size))
		if op is None:
			textImage = font.render(word, True, dray_gray)
			tw, th = textImage.get_size()
			dx=(block_size-bspace*2-tw)/2
			dy=(block_size-bspace*2-th)/2
			screen.blit(textImage, (dx+sx+ (n%block_num)*block_size,dy+sy+ (n/block_num)*block_size))
		n+=1

	pygame.display.update()