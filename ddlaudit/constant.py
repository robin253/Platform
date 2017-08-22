#!/bin/env python
# coding=UTF-8

import os

dict_config={
     'tabname_config':'T_',
     'indname_config': 'I_',
     'uniqindname_config':'IU_',
     'ind_max_colnum': 2,
     'seqname_config': 'SEQ_',
     'seqcache': 200,
     'seq_cycle_maxnum':10,
     'pkname_config': 'PK_',
     'pk_max_colnum': 2,
     'ukname_config': 'IU_',
     'uk_max_colnum': 2,
     'max_indnum_eachtable': 2,#不计入主键
     'data_tbs': 'USERS',
     'ind_tbs': 'USERS',
     'coltype_standard':['VARCHAR2','DATE','NUMBER','CHAR'],
     'coltype_total':['VARCHAR2','DATE','NUMBER','CHAR','CLOB','BLOB','NCLOB','NCHAR','TIMESTAMP','INT','LONG','NVARCHAR2','RAW','FLOAT'],
     'col_standard':['ID','CREATED_AT','CREATED_BY','UPDATED_AT','UPDATED_BY'],
     'col_reserved':['ACCESS','ADD','ALL','ALTER','AND','ANY','AS','ASC','AUDIT','BETWEEN','BY','CHAR','CHECK','CLUSTER',
                     'COLUMN','COMMENT','COMPRESS','CONNECT','CREATE','CURRENT','DATE','DECIMAL','DEFAULT','DELETE','DESC','DISTINCT','DROP',
                     'ELSE','EXCLUSIVE','EXISTS','FILE','FLOAT','FOR','FROM','GRANT','GROUP','HAVING','IDENTIFIED','IMMEDIATE','IN','INCREMENT',
                     'INDEX','INITIAL','INSERT','INTEGER','INTERSECT','INTO','IS','LEVEL','LIKE','LOCK','LONG','MAXEXTENTS','MINUS','MLSLABEL',
                     'MODE','MODIFY','NOAUDIT','NOCOMPRESS','NOT','NOWAIT','NULL','NUMBER','OF','OFFLINE','ON','ONLINE','OPTION','OR','ORDER',
                     'PCTFREE','PRIOR','PRIVILEGES','PUBLIC','RAW','RENAME','RESOURCE','REVOKE','ROW','ROWID','ROWNUM','ROWS','SELECT','SESSION',
                     'SET','SHARE','SIZE','SMALLINT','START','SUCCESSFUL','SYNONYM','SYSDATE','TABLE','THEN','TO','TRIGGER','UID','UNION','UNIQUE',
                     'UPDATE','USER','VALIDATE','VALUES','VARCHAR','VARCHAR2','VIEW','WHENEVER','WHERE','WITH'],
    }



