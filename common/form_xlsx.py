#!/usr/bin/env python
# -*- coding:utf-8 -*-

#制作xls备份文件
import xlsxwriter
import sys 
reload(sys) # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入 
sys.setdefaultencoding('utf-8') 

class Makexlsx():
    def __init__(self,filepath,filename):
        self.filename=filepath+'/'+filename
        self.workbook=xlsxwriter.Workbook(self.filename)


    #def makeformat(self):
        self.format=self.workbook.add_format() #定义内容格式
        self.format.set_border(1)              #定义单元格边框加粗（1像素）
        self.format.set_font_size(10)          #定义字体大小
        #self.format.set_num_format('0.00')     #定义数字类别显示格式


        self.format_title = self.workbook.add_format()                    #定义标题格式
        self.format_title.set_border(1)                                   #定义单元格边框加粗（1像素）
        self.format_title.set_font_size(11)                               #定义字体大小
        self.format_title.set_bold()                                      #定义对象单元格字体加粗
        self.format_title.set_bg_color('#5386D5')                         #定义单元格背景颜色
        self.format_title.set_align('center')                             #定义单元格居中对齐



    def add_worksheet(self,sheetname):

        self.sheet=self.workbook.add_worksheet(sheetname)
        self.sheet.set_column('A:J', 20) #设置列宽

    def insert_worksheet_title(self,list_titleinfo):
        self.sheet.write_row('A1',list_titleinfo,self.format_title) #list可变有序  dict 可变无序  元祖不可变有序

    def insert_worksheet_row(self,list_rowinfo):
        for i in range(len(list_rowinfo)):
            self.sheet.write_row(str('A'+str(i+2)),list_rowinfo[i],self.format)



    def close_workbook(self):
        self.workbook.close()


if __name__ == '__main__':
    testfile=Makexlsx("C:/","test.xlsx")
    testfile.add_worksheet('sheet1')
    testfile.insert_worksheet_title(['id','value'])
    testfile.insert_worksheet_row([['1','xulijia'],['2','wangjiachao'],['3','liangqi']])

    testfile.add_worksheet('sheet2')
    testfile.insert_worksheet_title(('num','code'))#输入元祖也可以的
    testfile.insert_worksheet_row([('1','19880506'),('2','19910101'),('3','19901220')])
    testfile.close_workbook()#记得关闭
    print "ok"


    

