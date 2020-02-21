# -*- coding=utf-8 -*-
import sys
import random
import pygame
from pygame.locals import *
from idiom_lib import IdiomLib

def run(mode):
	if sys.version_info < (3,0):
		reload(sys)
		sys.setdefaultencoding('utf-8')
	elif sys.version_info <= (3,3):
		import imp
		imp.reload(sys)
	else:
		import importlib
		importlib.reload(sys)

	# 横向和纵向上的文字数量
	block_num=12
	lib = IdiomLib(block_num=block_num)
	lib.load_idiom_from_file(mode=mode)

	# 顶部空出的像素（顶部空出的总高度是header_height+main_space）
	header_height = 30
	# 中间区域四周空出的像素
	main_space = 20

	# 每个文字的高度和宽度的像素值
	block_size = 36
	# 每个米字格往里缩多少像素
	bspace = 2
	space = 20
	# 总宽度=文字像素*文字数量+四周边距*2
	width = block_size * block_num + main_space * 2
	# 总高度=顶部高度+文字像素*文字数量+四周边距*2+底部待选区高度（即：文字像素*3+待选区两边留白space*3）
	height = header_height + block_size * block_num + main_space * 2 + block_size * 3 + space * 3

	pygame.init()
	screen = pygame.display.set_mode((width,height))

	title = (u'诗词填空',u'成语填空',u'英语单词填空')[mode-1]
	screencaption = pygame.display.set_caption(title)

	font = pygame.font.Font(u'syht.otf', int(block_size*0.8))

	dray_blue = 50,50,200
	white = 255,255,255
	#textImage = font.render(u'你好', True, white)

	# 加载和拉伸背景图片
	bg_image = pygame.image.load('bg.jpeg')
	bg_image = pygame.transform.scale(bg_image,(width, height))

	# 加载和拉伸中间区域的图片
	bg2_image = pygame.image.load('bg2.jpeg')
	bg2_image = pygame.transform.scale(bg2_image,(block_size*block_num,block_size*block_num))

	# 加载和拉伸每个汉字的米字格背景图片
	block_bg_image = pygame.image.load('tzg.jpg')
	block_bg_image = pygame.transform.scale(block_bg_image,(block_size-bspace*2,block_size-bspace*2))


	stage = 1
	lib.init(stage) # 初始化第一关

	# 获取文字宽度高度，以保证文字居中显示
	stage_textImage = pygame.font.Font(u'syht.otf', 30).render(u'第%s关'%stage, True, dray_blue)
	stage_font_width, stage_font_height = stage_textImage.get_size()
	stage_x = int((width - stage_font_width)/2)
	stage_y = int((header_height - stage_font_height)/2)+int(main_space/2)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()

			if event.type == MOUSEBUTTONDOWN:
				pressed_array = pygame.mouse.get_pressed()
				if pressed_array[0]:
					x, y = pygame.mouse.get_pos()

					# 计算选中的格子索引
					xi = (x - main_space) // block_size
					yi = (y - header_height - main_space) // block_size
					if xi>=0 and xi<block_num and yi>=0 and yi<block_num:
						# 提取选中格子的对象
						info = lib.matrix.get_val(xi, yi)
						# info=None的话格子是空的,info.state==1是已完成的句子不能点回去,info.hide_index>=0表示是下方点上来的文字
						if info and info.state != 1 and info.hide_index >= 0:
							if info.op_hide_index >= 0:
								lib.hide_arr[info.op_hide_index][-1] = None
								info.word = ''
								info.op_hide_index = -1
								lib.check_idiom()
							lib.select_rect = xi, yi

					sx = main_space
					sy = header_height + main_space+ block_size*block_num +space
					n = 0 # 下方选字区的文字序号
					# 这个循环主要用于判断鼠标是否点在下方选字区域的文字上
					for hi in range(len(lib.hide_arr)): # 遍历隐藏字列表
						tmp_x = sx + (n%block_num)*block_size # 第n个字的x方向起始像素位置
						tmp_y = sy + int(n/block_num)*block_size # 第n个字的y方向起始像素位置
						if lib.hide_arr[hi][-1] is None and x >= tmp_x and x <= tmp_x+block_size-bspace*2 and y >= tmp_y and y<= tmp_y+block_size-bspace*2:
							# 去除选中的代填文字上的对象
							info = lib.matrix.get_val(lib.select_rect[0],lib.select_rect[1])
							# 给对象赋值
							info.word = lib.hide_arr[hi][2]
							info.op_hide_index = hi # 记录下来源待选区域的位置,便于退出文字
							info.state = 0 # 还未完成的状态
							lib.hide_arr[hi][-1] = lib.select_rect
							# 选下一个推荐填充位置
							lib.select_rect = lib.get_next_select(lib.select_rect[0],lib.select_rect[1])
							flag = lib.check_idiom()
							if flag:
								stage += 1
								lib.init(stage)
								stage_textImage = pygame.font.Font(u'syht.otf', 30).render(u'第%s关'%stage, True, dray_blue)
							break
						n += 1

		screen.blit(bg_image, (0,0))
		screen.blit(stage_textImage, (stage_x,stage_y))

		# panel对应中间区域的画板
		panel = screen.subsurface((main_space,header_height+main_space,block_size*block_num,block_size*block_num))
		panel.blit(bg2_image, (0,0))

		# 对中间位置的文字进行绘制
		for i in range(block_num):
			for j in range(block_num):
				info = lib.matrix.get_val(i,j)
				if info is not None:
					bx = block_size*i+bspace
					by = block_size*j+bspace
					panel.blit(block_bg_image, (bx,by))

					if info.state == 1:
						textImage = font.render(info.word, True, (30,144,30)) # 正确完成的诗句上的字绿色
					elif info.is_lock == 1:
						textImage = font.render(info.word, True, (100,100,100)) # 不可点击灰色
					elif info.state == 2:
						textImage = font.render(info.word, True, (255,0,0)) # 错误红色
					else:
						textImage = font.render(info.word, True, dray_blue) # 默认蓝色

					tw, th = textImage.get_size()
					dx=int((block_size-bspace*2-tw)/2)
					dy=int((block_size-bspace*2-th)/2)
					panel.blit(textImage, (bx+dx,by+dy))
					if (i,j) == lib.select_rect: # 推荐填充位置填红色边框
						pygame.draw.rect(panel,(255,0,0),(bx,by,block_size-bspace*2,block_size-bspace*2),2)

		# 对下方待选文字区域的的文字进行绘制
		sx = main_space
		sy = header_height + main_space+ block_size*block_num +space
		n = 0
		for i,j,word,op in lib.hide_arr:
			screen.blit(block_bg_image, (sx + (n%block_num)*block_size,sy + int(n/block_num)*block_size))
			if op is None:
				textImage = font.render(word, True, dray_blue)
				tw, th = textImage.get_size()
				dx=int((block_size-bspace*2-tw)/2)
				dy=int((block_size-bspace*2-th)/2)
				screen.blit(textImage, (dx+sx+ (n%block_num)*block_size,dy+sy+ int(n/block_num)*block_size))
			n += 1

		pygame.display.update()

if __name__ == '__main__':
	run(mode=1)

