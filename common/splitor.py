# -*- coding:utf-8 -*-
import pygments.lexers.sql
from pygments.token import Token
import cStringIO

class LexerSplitor():
    def __init__(self):
        self.lexer = pygments.lexers.sql.PlPgsqlLexer() #lexer对象 语法解析
        self.buffer = cStringIO.StringIO()#StringIO的行为与file对象非常像，但它不是磁盘上文件，而是一个内存里的文件
        self.orginal_flush_tokens = (";")#结尾符 或者叫分隔符
        # 可回溯的 token 数量 
        self._last_token_max_count = 10
        # 记录token 
        self._last_token = []

    #函数：获取内存中的数据并清空内存
    def _get_sql_in_buffer_and_clean(self):
        _text = self.buffer.getvalue().strip()#读取
        self.buffer.seek(0) #定位第几个字符
        self.buffer.truncate()#清空内容
        return _text

    #函数：将token存入列表 超过最大长度那么就踢掉最旧的那个 先进先出
    def push_into_last_tokens(self, token):
        self._last_token.append(token)
        while len(self._last_token) > self._last_token_max_count:
            self._last_token.pop(0)

    #函数：输入文本 切分成单条SQL的list
    def split(self, text=None):
        sql_list = [] #存放每句sql_text的列表
        alter_or_drop = False        
        last_typ = None #上一个token的type
        last_val = None #上一个token的val
        flush_tokens = self.orginal_flush_tokens

        for current_token in self.lexer.get_tokens(text):#get_tokens解析成token流，包含两个属性：类型和值
            typ = current_token[0]#类型 一般有 Token.Name   [t1 col1]   Token.Punctuation [( ) ;]  Token.Operator [= /]
            #Token.Keyword  [insert into values update set where ] Token.Text [空格 换行]  
            #Token.Literal.Number.Float [ 4 5] Token.Literal.String.Single['  fds;// ]
            #Token.Comment.Single [--fdsf]   Token.Comment.Multiline[/*fdsfds fd*/  /*+parallel(4)*/]
            val = current_token[1]#值

            #根据情况修改flush_tokens 也就是结尾符 或者叫分隔符
            if Token.Keyword == typ and val.lower() in ("begin", "declare",):#出现begin或者declare的两个keyword的时候
                flush_tokens = ("/")

            if Token.Keyword == typ and val.lower() in ("alter", "drop",):#出现alter drop两个keyword的时候
                alter_or_drop = True
     
            if Token.Keyword == typ and val.lower() in ("procedure", "function", "package", "trigger"):
                if not alter_or_drop:
                    flush_tokens = ("/")
            #满足结尾符条件那么
            if (Token.Punctuation == typ and val in flush_tokens) \
                    or \
                    (Token.Operator == typ and val in flush_tokens  and last_typ == Token.Text):
                    #select 1/2 from dual;这种情况会误以为是结尾 添加 last_typ == Token.Text解决
                text = self._get_sql_in_buffer_and_clean()#将内存数据写入text  并清空内存
                if len(text) > 0:
                    sql_list.append(text)#text放入sql_text的列表中
                #将值还原重新开始循环
                flush_tokens = self.orginal_flush_tokens
                last_typ = None
                last_val = None
                alter_or_drop = False
                continue

            #不满足以上条件那么
            self.push_into_last_tokens(current_token)#记录token到_last_token列表 --这里没有使用到这个列表
            last_typ = typ#记录这个token的type
            last_val = val#记录这个token的val
            #将token的val值写入内存
            self.buffer.write(val.encode('utf-8'))

        # 最后将 buffer 中的也内容加进去
        text = self._get_sql_in_buffer_and_clean()
        if len(text) > 0:
            sql_list.append(text)

        return sql_list#返回存放每句sql_text的列表
    
    #函数：获取所有关键字合集，方便分析什么类型的语句 这里没有使用
    def get_keywords(self, text):
        key_word_list = []
        for token in self.lexer.get_tokens(text):
            if token[0] == Token.Keyword:
                key_word_list.append(token[1])
        return key_word_list

    #入参是一条sql的sqltext 
    #输出是去掉注释后的sqltext
    def remove_sqlcomment(self,onesqltext):
        token_list = []
        for token in self.lexer.get_tokens(onesqltext):
            if token[0] not in (Token.Comment.Multiline, Token.Comment.Single):
                token_list.append(token)

        for item_token in token_list:
            #typ = item_token[0]#类型 
            val = item_token[1]#值
            self.buffer.write(val.encode('utf-8'))
        
        new_sqltext=self._get_sql_in_buffer_and_clean()#获取内存中的数据并清空内存
        return new_sqltext



#测试
if __name__ == "__main__":
    lexerSplitor = LexerSplitor()
    sqltext = """
 --哈偶的
    /* en */
    /* wdd */
    select /* o
    k */ 1 from dual;


--ok
insert into /*test*/ my_procedure_tables values ( 1,2,3,4,5,6,7,8,9) /*tets111*/ ;



/*test*/
--en
insert into my_procedure_tables values /*test*/ ( 1,2,3,4,5,6,7,8,9) ;"""

    #输出切分好的全部单条SQL
    for sql in lexerSplitor.split(sqltext):
        print sql
        print "#withoutcomment:\n"
        print lexerSplitor.remove_sqlcomment(sql)
        print "===================================="