# -*- coding=utf-8 -*-
import os, sys
import random

if sys.version_info < (3,0):
    reload(sys)
    sys.setdefaultencoding('utf-8')
elif sys.version_info <= (3,3):
    import imp
    imp.reload(sys)
else:
    import importlib
    importlib.reload(sys)

def resource_path(relative):
	if hasattr(sys, "_MEIPASS"):
		absolute_path = os.path.join(sys._MEIPASS, relative)
	else:
		absolute_path = os.path.join(relative)
	return absolute_path

# 用于存放一条诗句的类
class IdiomInfo(object):
    def __init__(self,idiom):
        self.idiom = idiom # 诗句文本
        self.dire = 0 # 诗句方向 0 表示横向 1 表示纵向
        self.word_arr = [] # 诗句中每个汉字的WordInfo对象列表

    def to_str(self):
        arr = []
        for word_info in self.word_arr:
            arr.append('%s %s %s'%(word_info.i,word_info.j,word_info.word))
        return '%s,%s,%s'%(self.idiom, self.dire, '|'.join(arr))

# 用于存放单个文字的类
class WordInfo(object):
    def __init__(self, word, i, j):
        self.i = i # 文字所在的x坐标
        self.j = j # 文字所在的y坐标
        self.word = word # 文字内容
        self.is_lock = True # 文字是否需要填词
        self.state = -1
        self.hide_index = -1
        self.op_hide_index = -1

# 对应中间区域的格子数量构建的矩阵类，便于中间的文字管理
class Matrix(object):
    rows = 0 # 行数
    cols = 0 # 列数
    data = [] # 所有文字

    def __init__(self, rows, cols, data=None):
        self.rows = rows
        self.cols = cols
        if data is None: data = [None for i in range(rows * cols)]
        self.data = data

    # 设置文字
    def set_val(self, x, y, val):
        self.data[y * self.cols + x] = val

    # 获取文字
    def get_val(self, x, y):
        return self.data[y * self.cols + x]

    def exist_val_four_around(self, x, y, ignore_set):
        '''
        判断文字的四周是否有其他文字
        :param x: 列号
        :param y: 行号
        :param ignore_set: 需要忽略的格子
        :return:
        '''
        move_arr = [(-1,0),(1,0),(0,-1),(0,1)] # 左、右、上、下，四个方向

        for dx,dy in move_arr:
            tx = x + dx
            ty = y + dy
            if (tx,ty) in ignore_set: continue
            if tx < 0 or tx >= self.cols or ty <0 or ty >= self.rows: continue
            if self.data[ty * self.cols + tx]: return True
        return False

# 诗句操作库
class IdiomLib():
    def __init__(self, block_num=12):
        self.word_dic={} # 一个字有哪些诗句，格式为: {字:[诗句,诗句],……}
        self.word_arr=[] # 所有文字列表
        self.block_num=block_num # 横向和纵向上的格子数量
        self.matrix = Matrix(self.block_num, self.block_num) # 中间区域的文字矩阵
        self.idiom_dic={} # 当前关卡的诗句列表，格式为：{诗句:诗句对象IdiomInfo}
        self.all_word_num=0 # 当前关卡的文字数量
        self.hide_arr = [] # 当前关卡用于保存中间区域的缺字格子,列表类型：[[x,y,文字,None],……]

    # 从文件中加载诗句
    def load_idiom_from_file(self, mode=1):
        filename = ('poetry.txt','words.txt','english.txt')[mode-1]

        if sys.version_info < (3,0): 
            f = open(resource_path(filename))
        else:
            f = open(resource_path(filename),encoding='UTF-8')
        all_idiom = f.readlines()
        f.close()

        for idiom in all_idiom:
            if sys.version_info < (3,0):
                idiom = idiom.strip().decode('utf-8')
            else:
                idiom = idiom.strip()
            for word in idiom:
                if word not in self.word_dic: 
                    self.word_dic[word] = [idiom]
                else:
                    self.word_dic[word].append(idiom)

        self.word_arr = list(self.word_dic.keys())

    def check_new_idiom(self, new_idiom, new_dire, word_info):
        '''
        检查新新诗句是否有效，无效的场景 1.文字排开后发现超出边界 2.文字排开后发现和已选诗句的文字重叠
        :param new_idiom: 诗句
        :param new_dire: 诗句展开方向
        :param word_info: 当前的文字对象
        :return:
        '''
        windex = new_idiom.index(word_info.word)
        cx,cy = word_info.i, word_info.j
        ignore_set = set([(cx,cy)])

        new_idiom_word_arr=[]
        for i in range(-windex,-windex+len(new_idiom)): 
            if i==0: 
                new_idiom_word_arr.append(word_info)
            else:
                tx = cx+i  if new_dire == 0 else  cx
                # 横向超出边界
                if tx < 0 or tx >= self.block_num: return None,None

                ty = cy if new_dire == 0 else cy+i
                # 纵向超出边界
                if ty < 0 or ty >= self.block_num: return None,None

                # 抛掉第一个字外其他每一个字所在位置四周是否有文字
                if self.matrix.exist_val_four_around(tx, ty, ignore_set): return None,None

                old_word_info = self.matrix.get_val(tx, ty)
                if old_word_info:
                    return None,None

                new_word_info = WordInfo(new_idiom[i+windex], tx, ty)
                new_idiom_word_arr.append(new_word_info)

        return new_idiom_word_arr,windex

    def add_idiom_to_matrix(self, idiom_num):
        if idiom_num == 0: return 0
        for idiom,idiom_info in self.idiom_dic.items(): # 遍历已选定的诗句
            dire = idiom_info.dire
            new_dire = 1 - dire # 诗句横向纵向交替,因为横向=0,纵向=1,1-横向=纵向,1-纵向=横向
            for word_info in idiom_info.word_arr: # 遍历已选定的诗句中每个字
                word = word_info.word
                idiom_list = self.word_dic[word]
                for new_idiom in idiom_list: # 遍历这个字组成的诗句
                    if new_idiom in self.idiom_dic: continue # 如果诗句已经选定，跳过
                    new_idiom_word_arr,windex = self.check_new_idiom(new_idiom, new_dire, word_info) # 检查诗句有效性
                    if new_idiom_word_arr:
                        new_idiom_info = IdiomInfo(new_idiom)
                        new_idiom_info.dire = new_dire
                        # 对诗句的每个字在文字矩阵里放置
                        for new_index in range(len(new_idiom_word_arr)):
                            new_word_info = new_idiom_word_arr[new_index]
                            if new_index == windex:
                                new_idiom_info.word_arr.append(word_info)
                            else:
                                self.matrix.set_val(new_word_info.i, new_word_info.j , new_word_info)
                                new_idiom_info.word_arr.append(new_word_info)
                        self.idiom_dic[new_idiom] = new_idiom_info

                        # 继续增加下一个诗句
                        return len(new_idiom) -1 + self.add_idiom_to_matrix(idiom_num - 1)

        return 0

    def get_idiom_matrix(self, idiom_num):
        self.idiom_dic={}
        cx = int(self.block_num/2)-1
        cy = int(self.block_num/2)-1

        # 随机取一个字
        n = random.randint(0,len(self.word_arr)-1)
        word = self.word_arr[n]
        # 在这个字组成的诗句列表里取第一个诗句
        idiom = self.word_dic[word][0]
        wn = len(idiom)

        # 第一个诗句存到字典里
        self.idiom_dic[idiom] = IdiomInfo(idiom)

        # 对诗句的每个字在文字矩阵里放置
        for i in range(len(idiom)):
            word_info = WordInfo(idiom[i],cx-int(wn/2)+1+i,cy)
            self.matrix.set_val(cx-int(wn/2)+1+i,cy,word_info)
            self.idiom_dic[idiom].word_arr.append(word_info)

        # 添加下一个诗句
        wn += self.add_idiom_to_matrix(idiom_num-1)
        return wn

    def get_hide_arr(self, percent):
        self.hide_arr=[] # 用于保存中间区域的缺字格子,列表类型：[[x,y,文字,None],……]
        idiom_word_arr = [] # 列表类型：[[诗句,[文字对象,文字对象,……]],……]

        for k,v in self.idiom_dic.items():
            arr = []
            for word_info in v.word_arr:
                arr.append(word_info)
            idiom_word_arr.append([k, arr])
        # 按诗句的文字数量由多到少排序
        idiom_word_arr.sort(key=lambda x:-len(x[-1]))

        idiom_index = 0
        while len(self.hide_arr) < self.all_word_num*percent:
            tmp_arr = idiom_word_arr[idiom_index%len(idiom_word_arr)][1] # 取得一个诗句的一组文字
            n = random.randint(0,len(tmp_arr)-1) # 一组文字中随机取一个位置
            info = tmp_arr.pop(n) # 移除文字
            word=info.word
            info.word = '' # 格子上文字内容置空
            info.hide_index = len(self.hide_arr) # 记录下在文字隐藏列表中的位置索引
            info.is_lock = False # 格子上文字可点击
            self.hide_arr.append([info.i,info.j,word,None]) # 将文字加到隐藏列表
            idiom_index+=1 # 转到下一个诗句

        return self.hide_arr  

    def get_next_select(self, x, y):
        '''
        根据指定位置选取下一个默认选中格子
        :param x:
        :param y:
        :return:
        '''
        arr = []
        for i in range(self.block_num):
            for j in range(self.block_num):
                info = self.matrix.get_val(i, j)
                if info is not None and len(info.word) == 0:
                    dist = (i-x)*(i-x)+(j-y)*(j-y)
                    if i<x: dist+=0.2 # 格子在左，增加0.2距离，排序时会靠后
                    if j<y: dist+=0.4 # 格子在上，增加0.4距离，排序时会靠后
                    arr.append((i,j,dist))
        if len(arr) == 0:
            return None
        # 按所有可选格子的距离正序排序
        arr.sort(key=lambda x:x[-1])
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
        idiom_num = int(new_stage/5)+3
        if new_stage>100:
            percent = 0.7 # 100关以后隐藏文字的比例不再改变
        else:
            percent = 0.2+(new_stage*1.0/100)*(0.7-0.2)
        self.matrix = Matrix(self.block_num, self.block_num)
        # 生成一组诗句
        self.all_word_num = self.get_idiom_matrix(idiom_num)
        # 诗句中按比例提取一些隐藏字
        self.get_hide_arr(percent)
        # 默认选择中间区域第一个缺字的格子
        self.select_rect = self.hide_arr[0][0],self.hide_arr[0][1]

if __name__ == '__main__':
	pass
    # lib = IdiomLib(block_num=10)
    # lib.load_idiom_from_file()

    # arr = []
    # for i in range(1,101):
    #     lib.init(i)
    #     idiom_arr = []
    #     for k,v in lib.idiom_dic.items():
    #         idiom_arr.append(v.to_str())
    #     hide_arr = []
    #     for x,y,word,op in lib.hide_arr:
    #         hide_arr.append('%s %s %s'%(x,y,word))
    #     arr.append({'hide_num':len(hide_arr),'block_num':lib.block_num, 'word_num':lib.all_word_num,'idiom_arr':';'.join(idiom_arr),'hide_arr':';'.join(hide_arr)})
    # #arr.sort(cmp=lambda x,y:cmp(x['hide_num']*2+x['word_num'], y['hide_num']*2+y['word_num']))
    # arr.sort(key=lambda x:x['hide_num']*2+x['word_num'])

    # import json
    # f = open('idiom.json','w+') 
    # f.write(json.dumps(arr))
    # f.close()

