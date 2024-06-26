#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import sqlite3
import pandas as pd

SPSHEET_PATH = os.path.join(os.path.dirname(__file__), 'talleres.ods')
DBASE_PATH = os.path.join(os.path.dirname(__file__), 'wshop.db')

DAYS_LIST = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
TIMES_LIST = [('10:15', '11:15'), ('12:30', '13:30')]

#Convert ods table to dataframe and fix time coordinates
def ws_table(drop_c = False, nan_names=None):
    t = pd.read_excel(SPSHEET_PATH, sheet_name='talleres_ano')
    if nan_names is not None:
        t.loc[t['name'].isna(), 'name'] = nan_names
    t['coords'] = t.loc[:,'c1':'c3'].apply(row_coords, axis=1)
    if drop_c:
        t = t.drop(columns = t.loc[:,'c1':'c3'].columns)
    return t

def tup_from_cell_coord(s):
    assert isinstance(s,str)
    day_idx = {
        'lu': 0,
        'ma': 1,
        'mi': 2,
        'ju': 3,
        'vi': 4,
           }
    d, h = s[:2], s[2:]
    return (int(h)-1, day_idx[d.lower()])

def row_coords(row):
    r = row[row.notna()]
    return r.apply(tup_from_cell_coord).to_list()

def sort_by_day_time(t):
    df = pd.DataFrame(t.coords.str[0].to_list(), index=t.index)
    idx = df.sort_values([1,0]).index
    return t.loc[idx]

#Collision boolean table
def sample_collision(sample, df):
    return (df.astype("string") == str(sample)).any(axis=1)
    
def row_collision(row, df):
    bol = row.apply(sample_collision, df=df).any()
    return bol #df.loc[bol].index

def collision_df(series):
    'square boolean df with collisions'
    df = series.apply(pd.Series)
    return df.apply(row_collision, df=df, axis=1)

def boolean_collision_json(t):
    return collision_df(t.coords).to_json()

#DataBase

def dbase_connection():
    return sqlite3.connect(DBASE_PATH)

def create_inscription_table(t):
    con = dbase_connection()
    cur = con.cursor()
    ids = [f"ws_{i}" for i in t.index]
    ids_str = ', '.join(ids)
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS
        inscription (sname, cycle, {ids_str})
        """)
    con.commit()
    con.close()

def insert_to_dbase(sname, cycle, idx, t):
    con = dbase_connection()
    idx_bool_list = [0 for _ in t.index]
    for i in idx:
        idx_bool_list[i] = 1
    idx_str = ', '.join([str(i) for i in idx_bool_list])
    with con:
        con.execute(f"""
            INSERT INTO inscription
            VALUES ('{sname}', '{cycle}', {idx_str})
            """)
    con.close()

def read_from_dbase(t):
    con = dbase_connection()
    with con:
        res = con.execute("SELECT * FROM inscription")
    by_unique_name = {}
    for row in res.fetchall():
        by_unique_name[row[0]] = row[2:]
    ins = []
    for boolsidx in by_unique_name.values():
        ins.extend([i for i,v in enumerate(boolsidx) if v == 1])
    con.close()
    return [ins.count(i) for i in t.index]

def reset_dbase():
    con = dbase_connection()
    with con:
        con.execute("DELETE FROM inscription")
    con.close()

#if __name__ == '__main__':
    #pass
