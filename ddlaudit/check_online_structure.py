#!/bin/env python
# coding=UTF-8
from common import connect_oracle 


class CheckOnlineStructure():

    def __init__(self,username,password,ip,port,servicename):
        self.connection=connect_oracle.Oracle_Conn(username,password,ip,port,servicename)

    #ddl审核
    def check_objname(self,objname,objtype):
        sql='''select object_name,object_type from user_objects where object_name='{0}' and object_type='{1}' 
            '''.format(objname.upper(),objtype.upper())
        res=self.connection.execsql(sql)
        #print res
        if  isinstance(res,str):
            return 1
        elif isinstance(res,list) and len(res)!=1:
            return 1
        else:
            return 0

    #ddl审核
    def check_col(self,tablename,list_col):
        cols="','".join(list_col)
        cols="'"+cols+"'"
        cols=cols.upper()

        list_col_db=[]
        sql='''select column_name from user_tab_columns where table_name='{0}' and column_name in ({1})
             '''.format(tablename.upper(),cols)
        res=self.connection.execsql(sql)#None str list
        if isinstance(res,list):
            for item in res:
                list_col_db.append(item[0])
            #返回不存在的列
            return list(set(list_col)-set(list_col_db)) #差集   
        else:
            return "error"
        #返回线上表没有查到的列信息


    #ddl线上结构查询
    def check_tab(self,tabname_expression):
        sql='''select table_name from user_tables where table_name like '{0}'
             '''.format(tabname_expression.upper())
        res=self.connection.execsql(sql)#None str list
        if  isinstance(res,str):
            return None
        else:
            return res #返回表名

    
    def get_info(self,tabname):
        sql_tab='''select a.table_name,
              a.TABLESPACE_NAME,
              a.PARTITIONED,
              a.NUM_ROWS,
              a.AVG_ROW_LEN,
              to_char(a.last_analyzed,'YYYY-MM-DD'),
              b.COMMENTS table_comment
              from user_tables a, user_tab_comments b where a.table_name='{0}'
              and a.table_name=b.table_name'''.format(tabname.upper())
        res_tab=self.connection.execsql(sql_tab)
        if isinstance(res_tab,str):
            pass
        else:
            res_tab.insert(0,('表名','表空间','是否分区','行数','平均行字节','分析日期','注释'))
         


        sql_col='''
                select
                t.TABLE_NAME,
                t.COLUMN_NAME,
                decode(t.DATA_TYPE,'NUMBER',t.DATA_TYPE||'('||
                decode(t.DATA_PRECISION,null,t.DATA_LENGTH||')',t.DATA_PRECISION||','||t.DATA_SCALE||')'),
                'DATE',t.DATA_TYPE,'LONG',t.DATA_TYPE,'LONG RAW',t.DATA_TYPE,'ROWID',t.DATA_TYPE,
                'MLSLABEL',t.DATA_TYPE,t.DATA_TYPE||'('||t.DATA_LENGTH||')')  DATA_TYPE ,
                 NULLABLE,NUM_DISTINCT,NUM_NULLS,t1.COMMENTS col_comment
                from user_tab_columns t, user_col_comments t1 where t.table_name='{0}'
                and  t.table_name = t1.table_name and    t.column_name = t1.column_name
                order by column_id'''.format(tabname.upper())
        res_col=self.connection.execsql(sql_col)
        if isinstance(res_col,str):
            pass
        else:
            res_col.insert(0,('表名','字段名','数据类型','是否可空','DISTINCT值','空值记录数','列注释'))





        sql_ind='''select 
                   TABLE_NAME,
                   INDEX_NAME,
                   decode(UNIQUENESS,'NONUNIQUE','NO','YES'),
                   TABLESPACE_NAME,
                   BLEVEL,
                   --LEAF_BLOCKS,
                   DISTINCT_KEYS,
                   NUM_ROWS,
                   CLUSTERING_FACTOR,
                   PARTITIONED,
                    DEGREE,
                   (select b.ind_column  from 
                  (select index_name ,LISTAGG(column_name,',') within GROUP(order by column_position) as ind_column 
                    from user_ind_columns   group by index_name) b 
                   where a.index_name=b.index_name  ) ind_cols
                   from 
                  user_indexes a where table_name='{0}' order by 1,2'''.format(tabname.upper())
        res_ind=self.connection.execsql(sql_ind)
        if isinstance(res_ind,str):
            res_ind is None
        else:
            if res_ind!=[]:
                res_ind.insert(0,('表名','索引名','唯一性','表空间','层级'
                ,'DISTINCT值','行数','聚簇因子','是否分区','并行度','索引列'))




        sql_tab_part='''
                     select  table_name, partition_count,partitioning_type,
                     subpartitioning_type,def_tablespace_name,interval, 
                     (select  column_name from user_part_key_columns where  name='{0}') PAR_KEY,
                     (select column_name from user_subpart_key_columns where  name='{1}') SUBPAR_KEY
                     from  user_part_tables where  table_name='{2}'
                      '''.format(tabname.upper(),tabname.upper(),tabname.upper())
        res_tab_part=self.connection.execsql(sql_tab_part)
        if isinstance(res_tab_part,str):
            res_tab_part is None
        else:
            if res_tab_part!=[]:
                res_tab_part.insert(0,('表名','分区数','分区类型','子分区类型'
                ,'默认表空间','间隔','分区键','子分区键'))



        sql_ind_part='''select table_name,index_name,partition_count,partitioning_type,SUBPARTITIONING_TYPE,
                        locality,def_tablespace_name,interval
                       from user_part_indexes where table_name='{0}'
                      '''.format(tabname.upper())
        res_ind_part=self.connection.execsql(sql_ind_part)
        if isinstance(res_ind_part,str):
            res_ind_part is None
        else:
            if res_ind_part!=[]:
                res_ind_part.insert(0,('表名','索引名','分区数','分区类型','子分区类型',
                '索引类型','默认表空间','间隔'))


        return res_tab,res_col,res_ind,res_tab_part,res_ind_part


    def close(self):
        self.connection.close_commit()



if __name__ == '__main__':
    try:
       checkobj=CheckOnlineStructure("xulijia","xulijia",'192.168.152.244','1521','orcl')
    except:
        print "connect wrong"
    else:
        print checkobj.check_objname("TTEST1","TABLE")
        print checkobj.check_objname("SEQ_PMT_BIZ_ERROR","SEQUENCE")
        print checkobj.check_col("T2",['INDEX','OBJECT_ID','TEST','OBJECT_NAME'])
        checkobj.close()