#!/bin/env python
# -*- coding: UTF-8 -*-

from common.connect_oracle  import Oracle_Conn
import os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'#防止oracle中文返回出现乱码
import copy



class check():


 
    
    def __init__(self,username,password,ipadress,port,servicename,dict_config):
        self.connection=Oracle_Conn(username,password,ipadress,port,servicename)

        #configuration#
        self.dict_config=dict_config
    
    #tables
    def tables_info(self):
        """get tables info"""
        return    ''' select table_name,tablespace_name,'NO' partitioned
                    from user_tables where table_name not like 'BIN$%' 
                    and table_name not like '%BAK%' 
                    and table_name not like '%TMP%'
                    and table_name not like '%TEMP%' 
                    and partitioned='NO'
                   union all
                  select distinct table_name,tablespace_name,'YES' partitioned
                    from user_tab_partitions where table_name not like 'BIN$%' 
                    and table_name not like '%BAK%' 
                    and table_name not like '%TMP%'
                    and table_name not like '%TEMP%' 
                    '''
    def tables_notpartition(self):
        """big tables but not partitioned"""
        return    ''' select table_name from user_tables where partitioned='NO' 
                              and table_name not like 'BIN$%' 
                              and table_name not like '%BAK%' 
                              and table_name not like '%TMP%'
                              and table_name not like '%TEMP%' 
                              and num_rows>{0} '''.format(int(self.dict_config['max_row_eachtable']))
    
    def tables_notinterval(self):
        """tables range partitioned interval status"""
        return      ''' select table_name,partition_count from user_part_tables 
                             where table_name not like 'BIN$%'
                             and table_name not like '%BAK%' 
                             and table_name not like '%TMP%'
                             and table_name not like '%TEMP%' 
                             and interval is null and  partitioning_type ='RANGE' '''
    def tables_datatype(self):
        """tables columns datatype"""
        return       ''' select c.table_name,c.column_name,c.data_type
                         from user_tab_columns c,user_tables t
                        where t.table_name=c.table_name 
                         and t.table_name not like 'BIN$%' 
                        and t.table_name not like '%BAK%' 
                        and t.table_name not like '%TMP%'
                        and t.table_name not like '%TEMP%' 
                        and data_type not in ({0}) '''.format(self.dict_config['standard_datatype'])
    
    def tables_colcnt(self):
        """tables columns count"""
        return      ''' select c.table_name,count(*) from user_tab_columns c,user_tables t
                       where c.table_name=t.table_name  
                        and t.table_name not like 'BIN$%' 
                        and t.table_name not like '%BAK%' 
                        and t.table_name not like '%TMP%'
                        and t.table_name not like '%TEMP%' 
                        group by c.table_name having count(*)> {0}'''.format(self.dict_config['max_colnum_eachtable'])
    

    def  tables_standard_cols(self):                                                                                                                                                                            
        """tables standard columns"""
        return        '''select a.table_name,count(b.column_name)
                            from user_tables a left join user_tab_columns b 
                            on a.table_name=b.table_name
                            and b.column_name||','||b.data_type in ({0}) 
                            where  a.table_name not like 'BIN$%'
                            and  a.table_name not like '%BAK%' 
                            and  a.table_name not like '%TMP%'
                            and  a.table_name not like '%TEMP%'
                            group by  a.table_name having count(b.column_name)!=5'''.format(self.dict_config['standard_cols'])

    def tables_indexcnt(self):
        """tables indexes count"""
        return     ''' select a.table_name,count(b.index_name)
                    from user_tables a left join user_indexes b on a.table_name=b.table_name
                    and   b.index_type not in ('LOB')
                    where  a.table_name not like 'BIN$%'
                          and  a.table_name not like '%BAK%' 
                          and  a.table_name not like '%TMP%'
                          and  a.table_name not like '%TEMP%'
                    group by a.table_name
                    '''

    def tables_primarykey(self):
        """tables  primary key"""
        return       '''
                        select a.table_name,b.constraint_name,b.status,b.validated
                          from user_tables a left join user_constraints b on a.table_name=b.table_name
                          and b.constraint_type='P'
                          where  a.table_name not like 'BIN$%'
                          and  a.table_name not like '%BAK%' 
                          and  a.table_name not like '%TMP%'
                          and  a.table_name not like '%TEMP%'
                          '''  


    #indexes
    def indexes_info(self):
        """get indexes info """
        return  '''select table_name, index_name, uniqueness,tablespace_name,degree, 'NO' PARTITIONED from user_indexes
                    where partitioned = 'NO' and index_type not in ('LOB')
                    and  table_name not like 'BIN$%'
                    and  table_name not like '%BAK%' 
                    and  table_name not like '%TMP%'
                    and  table_name not like '%TEMP%'
                    union all
                   select distinct b.table_name,a.index_name,b.uniqueness,a.tablespace_name, b.degree,'YES' PARTITIONED
                     from user_ind_partitions a, user_indexes b
                    where a.index_name = b.index_name and b.partitioned = 'YES' 
                    and index_type not in ('LOB')
                    and  b.table_name not like 'BIN$%'
                    and  b.table_name not like '%BAK%' 
                    and  b.table_name not like '%TMP%'
                    and  b.table_name not like '%TEMP%'
                       '''
    def indexes_pk(self):
        """get indexes pk"""
        return '''
                  select a.table_name,b.index_name
                          from user_tables a ,user_constraints b where a.table_name=b.table_name
                          and b.constraint_type='P' and index_name is not null
                          and   a.table_name not like 'BIN$%'
                          and  a.table_name not like '%BAK%' 
                          and  a.table_name not like '%TMP%'
                          and  a.table_name not like '%TEMP%'
                '''

    def indexes_unnormal(self):
        """indexes unnormal"""
        return '''select table_name,index_name,index_type 
                          from user_indexes where index_type not in ('NORMAL','LOB') and table_name not like 'BIN$%'
                          and table_name not like '%BAK%' and table_name not like '%TMP%'
                          and table_name not like '%TEMP%'
                        '''

    def indexes_colcnt(self):
        """indexes columns count"""
        return       '''select table_name,index_name,count(*) from user_ind_columns
                        where table_name not like 'BIN$%' and table_name not like '%BAK%' and table_name not like '%TMP%'
                        and table_name not like '%TEMP%'
                        group by table_name,index_name'''


    def indexes_locality(self):
        """indexes (partition table) locality status"""
        return  '''select a.table_name, a.index_name, a.partitioned, nvl(b.locality,'GLOBAL') locality
                        from (select i.table_name, i.index_name, i.partitioned
                                 from user_indexes i, user_tables t
                                where i.table_name = t.table_name
                                  and t.partitioned = 'YES'
                                  and i.index_type not in ('LOB')
                                  and t.table_name not like 'BIN$%'
                                  and t.table_name not like '%BAK%' 
                                  and t.table_name not like '%TMP%'
                                  and t.table_name not like '%TEMP%') a
                        left join user_part_indexes b on b.index_name = a.index_name  and b.table_name=a.table_name'''

    def indexes_redundant(self):
        """indexes redundant"""
        return '''select b.table_name, b.index_name, b.column_name, a.index_name, a.column_name
                             from
                                  (select table_name, index_name,
                                    LISTAGG(column_name,',') within GROUP(order by column_position) as column_name
                                      from user_ind_columns
                                     where table_name not like 'BIN$%'
                                      and table_name not like '%BAK%' 
                                      and table_name not like '%TMP%'
                                      and table_name not like '%TEMP%'
                                     group by table_name, index_name) a,
                                   (select table_name, index_name,
                                    LISTAGG(column_name,',') within GROUP(order by column_position) as column_name
                                      from user_ind_columns
                                     where table_name not like 'BIN$%'
                                      and table_name not like '%BAK%' 
                                      and table_name not like '%TMP%'
                                      and table_name not like '%TEMP%'
                                     group by table_name, index_name) b
                            where a.table_name = b.table_name
                              and a.index_name != b.index_name
                              and a.column_name like b.column_name||'%' '''

    #sequences
    def sequences_info(self):
        """sequences"""
        return  "select sequence_name,cycle_flag,order_flag,cache_size,round(last_number/max_value,2)*100 from user_sequences"



    #commments
    def comments_table(self):
        """comments table"""
        return '''select table_name from user_tab_comments where comments is null and table_type='TABLE' and 
                     table_name not like 'BIN$%' and table_name not like '%BAK%' and table_name not like '%TMP%'
                     and table_name not like '%TEMP%'
                  '''
    def comments_tablecol(self):
        """comments tablecolumn"""
        return '''select table_name, 
                         to_char(WMSYS.WM_CONCAT(column_name)) as column_name,
                         to_char(WMSYS.WM_CONCAT(comment_column)) as comment_column
                         from (
                         select a.table_name,a.column_name,
                               (case 
                                when b.comments is null 
                                then '' 
                                else b.column_name 
                                end) COMMENT_COLUMN  
                        from user_tab_cols a ,user_col_comments b 
                        where a.table_name=b.table_name
                        and a.column_name=b.column_name
                        and a.table_name not like 'BIN$%' 
                        and a.table_name not like '%BAK%' 
                        and a.table_name not like '%TMP%'
                        and a.table_name not like '%TEMP%')
                        group by table_name
                       '''





    def check_elements(self,list_elementcheck,tablespacecheck,standardcolcheck):#['tables','indexes','comments','sequences']

        checklist=[]
        for item in dir(check): #dir inspect getattr都比较有用
            #print item
            for element in list_elementcheck:
                if item.startswith(element):    
                    checklist.append(item)
        #print checklist

        dict_return={}
        for  item in checklist:
            funcname="self."+item
            #print funcname
            sqlres = self.connection.execsql(eval(funcname)())
            if isinstance(sqlres,list):
                dict_return[item]=copy.deepcopy(sqlres)
            else:
                pass

        self.connection.close_commit()

        #开始审核逻辑

        #表
        dict_table={}
        if "tables" in list_elementcheck:
            data_tbs=self.dict_config['data_tbs']

            #检查表名和表空间 tables_info
            for i in dict_return['tables_info']:
                dict_table[i[0]]=[]
                if not i[0].startswith(self.dict_config['tabname']):
                    dict_table[i[0]].append("表名不规范，应以"+str(self.dict_config['tabname'])+"开头；")
                if tablespacecheck=='tablespacecheck':
                    if i[1]!=data_tbs:
                        dict_table[i[0]].append("使用了"+str(i[1])+"表空间，应使用"+str(data_tbs)+"表空间；")
                else:
                    pass


            #检查大表没有分区 tables_notpartition
            for i in dict_return['tables_notpartition']:
                dict_table[i[0]].append("非分区表"+str(i[0])+"超过"+str(self.dict_config['max_row_eachtable'])+"行，请考虑进行分区处理；")


            #检查range分区表非间隔分区 tables_notinterval
            for i in dict_return['tables_notinterval']:
                dict_table[i[0]].append("分区表"+str(i[0])+"分区数为"+str(i[1])+"，不是间隔分区，请检查是否需要扩分区；")

            #检查表的列类型合规 tables_datatype
            for i in dict_return['tables_datatype']:
                dict_table[i[0]].append(str(i[1])+"字段使用了不合规的类型"+str(i[2])+"；")

            #表的总列数 tables_colcnt
            for i in dict_return['tables_colcnt']:
                dict_table[i[0]].append("本表超过"+str(self.dict_config['max_colnum_eachtable'])+"个字段；")
            

            #是否有标准列 tables_standard_cols
            if standardcolcheck=='standardcolcheck':
                for i in dict_return['tables_standard_cols']:
                    dict_table[i[0]].append("本表没有创建全部标准列；")


            #检查表的索引数量 tables_indexcnt
            for i in dict_return['tables_indexcnt']:
                if i[1]>int(self.dict_config['max_indnum_eachtable']):
                    dict_table[i[0]].append("本表有"+str(i[1])+"个索引，超过"+str(self.dict_config['max_indnum_eachtable'])+"个，请确认索引必要性；")
                elif i[1]==0:
                    dict_table[i[0]].append("表上没有任何索引，请关注；")


            #表的主键 tables_primarykey
            for i in dict_return['tables_primarykey']:
                if i[1] is None:
                    dict_table[i[0]].append("本表没有主键约束，请添加；")
                elif i[1] is not None and i[2]=='DISABLED':
                    dict_table[i[0]].append("本表的主键约束"+str(i[1])+"已DISABLED；")#此时index_name为空
                elif i[1] is not None and i[2]=='ENABLED' and i[3]=='NOT VALIDATED':
                    dict_table[i[0]].append("本表的主键约束"+str(i[1])+"创建时为NOT VALIDATED；")
                else:
                    pass

        #索引(主键索引)
        dict_ind={} #用于记录全部索引
        dict_pk={} #用于记录主键索引
        if "indexes" in list_elementcheck:

            ind_tbs=self.dict_config['ind_tbs']
            #主键索引 indexes_pk
            for i in dict_return['indexes_pk']:
                dict_pk[i[0]+"."+i[1]]=[]


            #索引 indexes_info
            for i in dict_return['indexes_info']:
                tab_ind_name=i[0]+"."+i[1]
                dict_ind[tab_ind_name]=[]
                if tab_ind_name not in dict_pk.keys():
                    if tablespacecheck=='tablespacecheck':
                        if i[3]!=ind_tbs:
                            dict_ind[tab_ind_name].append("该索引使用了"+str(i[3])+"表空间，应该使用"+str(ind_tbs)+"表空间；")
                    if i[2]=='NONUNIQUE' and not i[1].startswith(self.dict_config['indname']):
                        dict_ind[tab_ind_name].append("该索引名不规范，应以"+str(self.dict_config['indname'])+"开头；")
                    if i[2]=='UNIQUE' and not i[1].startswith(self.dict_config['uniqindname']):
                        dict_ind[tab_ind_name].append("该索引名不规范，唯一索引应以"+str(self.dict_config['uniqindname'])+"开头；")
                    if int(i[4])!=1 or i[4]=='default':
                        dict_ind[tab_ind_name].append("该索引上有"+str(i[4])+"个并行度,请关闭；")
                else:
                    if tablespacecheck=='tablespacecheck':
                        if i[3]!=ind_tbs:
                            dict_ind[tab_ind_name].append("该主键索引使用了"+str(i[3])+"表空间，应该使用"+str(ind_tbs)+"表空间；")
                    if not i[1].startswith(self.dict_config['pkname']):
                        dict_ind[tab_ind_name].append("该主键索引不规范，应以"+str(self.dict_config['pkname'])+"开头；")
                    if int(i[4])!=1 or i[4]=='default':
                        dict_ind[tab_ind_name].append("该主键索引上有"+str(i[4])+"个并行度,请关闭；")
                    if i[2]=='NONUNIQUE':
                        dict_ind[tab_ind_name].append("该主键索引非唯一索引")

            #非普通索引 indexes_unnormal
            for i in dict_return['indexes_unnormal']:
                tab_ind_name=i[0]+"."+i[1]
                dict_ind[tab_ind_name].append("该索引是"+str(i[2])+"索引，不要使用非普通索引，请改造；")



            #索引字段过多 indexes_colcnt
            for i in dict_return['indexes_colcnt']:
                tab_ind_name=i[0]+"."+i[1]
                if tab_ind_name not in dict_pk.keys():
                    if i[2]>int(self.dict_config['ind_max_colnum']):
                        dict_ind[tab_ind_name].append("该索引联合列超过"+str(self.dict_config['ind_max_colnum'])+"个，请关注；")
                else:
                    if i[2]>int(self.dict_config['pk_max_colnum']):
                        dict_ind[tab_ind_name].append("该主键索引联合列超过"+str(self.dict_config['pk_max_colnum'])+"个，请关注；")
            
            #分区表的索引不是本地的 indexes_locality
            for i in dict_return['indexes_locality']:
                tab_ind_name=i[0]+"."+i[1]
                if not (i[2]=='YES'  and i[3]=='LOCAL') :
                    dict_ind[tab_ind_name].append("在分区表上不要使用全局索引，请改造；")


            #冗余索引 indexes_redundant
            for i in dict_return['indexes_redundant']:
                tab_ind_name=i[0]+"."+i[1]
                dict_ind[tab_ind_name].append("该索引（"+str(i[2])+")是一个冗余索引,它可以被"+str(i[3])+"索引("+str(i[4])+")替代，建议删除该索引；")

            
        #序列
        dict_sequence={}
        if "sequences" in list_elementcheck:

            #序列信息 sequences_info
            for i in dict_return['sequences_info']:
                dict_sequence[i[0]]=[]
                if not i[0].startswith(self.dict_config['seqname']):
                    dict_sequence[i[0]].append("序列名不规范，应以"+str(self.dict_config['seqname'])+"开头；")
                #if i[1]=='Y':
                # dict_sequence[i[0]].append("本序列使用了CYCLE属性")
                if i[2]=='Y':
                    dict_sequence[i[0]].append("序列使用了ORDER属性，不允许；")
                if i[3]<int(self.dict_config['seqcache']):
                    dict_sequence[i[0]].append("本序列CACHE值小于"+str(self.dict_config['seqcache'])+"，请关注；")
                if i[4]>int(self.dict_config['seq_usedrate']) and i[1]=='N':
                    dict_sequence[i[0]].append("本序列使用率达"+str(self.dict_config['seq_usedrate'])+"，请关注；")


        #注释    
        dict_comment={}
        if "comments" in list_elementcheck:

            #表注释 comments_table
            for i in dict_return['comments_table']:
                dict_comment[i[0]]=[]
                dict_comment[i[0]].append("本表无表级注释；")

            #列注释 comments_tablecol
            for i in dict_return['comments_tablecol']:
                if dict_comment.has_key(i[0]):
                    pass
                else:
                    dict_comment[i[0]]=[]
               

                if i[2] is None:
                    dict_comment[i[0]].append("本表没有任何列注释；")
                elif i[2] is not None:
                    list_column=i[1].split(",") 
                    list_comment_column=i[2].split(",")
                    #print list_column
                    #print list_comment_column
                    ret = [ ii for ii in list_column if ii not in list_comment_column ]
                    strret=','.join(ret)
                    if strret:
                        dict_comment[i[0]].append("本表的"+strret+"列没有注释；")


        list_returninfo=[]
        for key in dict_table:
          if dict_table[key]:
              list_returninfo.append({'object':key,'object_type':'TABLE','problem':'\n'.join(dict_table[key])})
        for key in dict_ind:
          if dict_ind[key]:
              list_returninfo.append({'object':key,'object_type':'INDEX','problem':'\n'.join(dict_ind[key])})
        for key in dict_sequence:
          if dict_sequence[key]:
              list_returninfo.append({'object':key,'object_type':'SEQUENCE','problem':'\n'.join(dict_sequence[key])})
        for key in dict_comment:
          if dict_comment[key]:
              list_returninfo.append({'object':key,'object_type':'COMMENT','problem':'\n'.join(dict_comment[key])})

        return list_returninfo



