# -*- coding:utf-8 -*-
import os


#awr ash文件路径
reportfile_path=os.path.join(os.path.dirname(__file__), 'reportfiles').replace('\\', '/')#\变成/



#对象审核的配置参数
dict_config={
     'tabname':'T_',
     'indname': 'I_',
     'uniqindname':'IU_',
     'ind_max_colnum': '3',
     'seqname': 'SEQ_',
     'seqcache': '200',
     'seq_usedrate': '70',
     'seq_len':'10',
     'pkname': 'PK_',
     'pk_max_colnum': '2',
     'max_indnum_eachtable': '3',
     'max_colnum_eachtable':'40',
     'max_row_eachtable':'500000',
     'standard_cols':"'ID,NUMBER','CREATED_AT,DATE','CREATED_BY,VARCHAR2','UPDATED_AT,DATE','UPDATED_BY,VARCHAR2'",
     'standard_datatype':"'VARCHAR2','DATE','NUMBER','CHAR'",
     'data_tbs':'USERS',
     'ind_tbs':'USERS'}