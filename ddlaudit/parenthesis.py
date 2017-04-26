#!/bin/env python
# coding=UTF-8




#find_cont_firstparenthesis函数
#返回字符串中第一个括号组中的内容
def find_cont_firstparenthesis(sqltext):
    def findbeforestrcount(oristr,serchstr,position):#找字符串某位置之前有多少个serchstr字符
        str=oristr[0:position]
        #print str
        x=str.count(serchstr)
        return x
    #找字符串某位置之后有多少个serchstr字符  oristr.count(serchstr,position)就可以了

    
    an=sqltext.count("(") #查看左右括号的数量
    bn=sqltext.count(")") 
    at=sqltext.find("(") #找到第一个左右括号的位置
    bt=sqltext.find(")")
    #print an,bn,at,bt

    restr=""
    flag=0
    if an==0 or bn==0:
        restr=restr+"没有左括号或右括号\n"
        flag=1
    if an!=bn:
        restr=restr+"左右括号的数量不相等\n"
        flag=1
    if at>bt and at>0 and bt>0:
        restr=restr+"先有右括号再有左括号\n"
        flag=1

    if flag==1:
        restr="语法错误:\n"+restr
    else:
        pass

    if flag==0:
        y=1 #右括号的计数
        while 1:
            x=findbeforestrcount(sqltext,"(",bt)#找一个右括号之前都多少个左括号
            if x>y: #如果左括号的个数大于右括号的个数，那么继续
                y=y+1
                bt=sqltext.find(")",bt+1) #找到后一个右括号的位置
                #print bt
                continue
            elif x==y:                    #个数相等的时候 那么可以获取内容了
                break
        if sqltext[at+1:bt]=="":
            flag=1
            restr="第一个括号中没有内容"
            return flag,at,bt,restr         #第一个括号中内容为空那么也返回错误
        else:
            return flag,at,bt,sqltext[at+1:bt] #最终返回第一个括号组中的内容
    else:
        return flag,at,bt,restr  #如果语法错误那么返回错误的原因


#remove_cont_parenthesis函数
#删除字符串中所有括号和括号里面的内容 
def  remove_cont_parenthesis(sqltext):
    sqltmp=""
    sqlreturn=""
    an=sqltext.count("(") #查看左右括号的数量
    bn=sqltext.count(")") 
    at=sqltext.find("(") #找到第一个左右括号的位置
    bt=sqltext.find(")")
    #print an,bn,at,bt
   
    if an!=bn:
        return sqltext
    elif an==bn and an==0:
        return sqltext
    
    elif an==bn and an!=0:
        i=1    
        while i<=an :
            sqltmp=sqltext[0:at]
            sqltext=sqltext[bt+1:]
            sqlreturn=sqlreturn+sqltmp
            if i==an:
                sqlreturn=sqlreturn+sqltext
            at=sqltext.find("(")
            bt=sqltext.find(")")
            i=i+1
        
        return sqlreturn

#x='col number(20),col2 varchar2(20) not null,col3 date default sysdate'
#y=remove_cont_parenthesis(x)
#print y

