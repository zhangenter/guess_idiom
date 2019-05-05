# -*- coding=utf-8 -*-
import sys
import random
import pygame
from pygame.locals import *
from idiom_lib import IdiomLib
reload(sys)
sys.setdefaultencoding('utf-8')

block_num=12
lib = IdiomLib(block_num=block_num)
lib.load_idiom_from_file()

header_height = 30
main_space = 20

block_size = 36
bspace = 2
space = 20
width = block_size * block_num + main_space * 2
height = header_height + block_size * block_num + main_space * 2 + (block_size+space) * 3

pygame.init()
screen = pygame.display.set_mode((width,height))
screencaption = pygame.display.set_caption(u'成语填空')

font = pygame.font.Font(u'syht.otf', int(block_size*0.8))

dray_gray = 50,50,200
white = 255,255,255
#textImage = font.render(u'你好', True, white)

bg_image = pygame.image.load('bg.jpeg')
bg_image = pygame.transform.scale(bg_image,(width, height))

bg2_image = pygame.image.load('bg2.jpeg')
bg2_image = pygame.transform.scale(bg2_image,(block_size*block_num,block_size*block_num))

block_bg_image = pygame.image.load('tzg.jpg')
block_bg_image = pygame.transform.scale(block_bg_image,(block_size-bspace*2,block_size-bspace*2))


stage = 1
lib.init(stage)
stage_textImage = pygame.font.Font(u'syht.otf', 30).render(u'第%s关'%stage, True, dray_gray)
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
							info = lib.matrix.get_val(i, j)
							if info and info.state != 1 and info.hide_index >= 0:
								if info.op_hide_index>=0:
									lib.hide_arr[info.op_hide_index][-1] = None
									info.word = ''
									info.op_hide_index=-1
									lib.check_idiom()
								lib.select_rect = i,j
								break

				sx = main_space
				sy = header_height + main_space+ block_size*block_num +space
				n = 0
				for hi in range(len(lib.hide_arr)):
					tmp_x = sx + (n%block_num)*block_size
					tmp_y = sy + (n/block_num)*block_size
					if lib.hide_arr[hi][-1] is None and x >= tmp_x and x <= tmp_x+block_size-bspace*2 and y >= tmp_y and y<= tmp_y+block_size-bspace*2:
						info = lib.matrix.get_val(lib.select_rect[0],lib.select_rect[1])
						info.word = lib.hide_arr[hi][2]
						info.op_hide_index = hi
						info.state = 0
						lib.hide_arr[hi][-1] = lib.select_rect
						lib.select_rect = lib.get_next_select(lib.select_rect[0],lib.select_rect[1])
						flag = lib.check_idiom()
						if flag:
							stage += 1
							lib.init(stage)
							stage_textImage = pygame.font.Font(u'syht.otf', 30).render(u'第%s关'%stage, True, dray_gray)
						break

					n += 1


	screen.blit(bg_image, (0,0))
	screen.blit(stage_textImage, (stage_x,stage_y))

	panel = screen.subsurface((main_space,header_height+main_space,block_size*block_num,block_size*block_num))
	panel.blit(bg2_image, (0,0))

	for i in range(block_num):
		for j in range(block_num):
			info = lib.matrix.get_val(i,j)
			if info is not None:
				bx = block_size*i+bspace
				by = block_size*j+bspace
				panel.blit(block_bg_image, (bx,by))
				
				if info.state == 1:
					textImage = font.render(info.word, True, (30,144,30))
				elif info.is_lock == 1:
					textImage = font.render(info.word, True, (100,100,100))
				elif info.state == 2:
					textImage = font.render(info.word, True, (255,0,0))
				else:
					textImage = font.render(info.word, True, dray_gray)

				tw, th = textImage.get_size()
				dx=(block_size-bspace*2-tw)/2
				dy=(block_size-bspace*2-th)/2
				panel.blit(textImage, (bx+dx,by+dy))
				if (i,j) == lib.select_rect:
					pygame.draw.rect(panel,(255,0,0),(bx,by,block_size-bspace*2,block_size-bspace*2),2)

	sx = main_space
	sy = header_height + main_space+ block_size*block_num +space
	n = 0
	for i,j,word,op in lib.hide_arr:
		screen.blit(block_bg_image, (sx + (n%block_num)*block_size,sy + (n/block_num)*block_size))
		if op is None:
			textImage = font.render(word, True, dray_gray)
			tw, th = textImage.get_size()
			dx=(block_size-bspace*2-tw)/2
			dy=(block_size-bspace*2-th)/2
			screen.blit(textImage, (dx+sx+ (n%block_num)*block_size,dy+sy+ (n/block_num)*block_size))
		n+=1

	pygame.display.update()