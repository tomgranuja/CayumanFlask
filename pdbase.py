#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import json
import pandas as pd

#Convert ods table to dataframe and fix time coordinates
def ws_table(drop_c = False):
    t = pd.read_excel('talleres.ods', sheet_name='talleres_ano')
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

#Export workshop data to javascript and write to local file.
def export_json_data():
    var_names = {
        'ulmos': {'bool': 'ulmos_collision', 
                  'ws':'ulmos_ws',
                  'idx': 'ulmos_idx'},
        'canelos y manios': {'bool': 'manelos_collision',
                             'ws': 'manelos_ws',
                             'idx': 'manelos_idx'},
        'coihues y avellanos': {'bool': 'coillanos_collision',
                                'ws':'coillanos_ws',
                                'idx': 'coillanos_idx'},
    }
    to = ws_table(drop_c = True)
    lines = []
    for c in var_names:
        t = to[to.cycle == c]
        json_bool = collision_df(t.coords).to_json()
        json_ws = t.drop(columns='coords').to_json()
        json_idx = json.dumps(t.index.to_list())
        js = (
            f"const {var_names[c]['bool']} = JSON.parse('{json_bool}')\n"
            f"const {var_names[c]['ws']} = JSON.parse('{json_ws}')\n"
            f"const {var_names[c]['idx']} = JSON.parse('{json_idx}')"
        )
        lines.append(js)
    
    with open('workshops.js', 'w') as f:
        f.write('\n'.join(lines))
    with open('workshops.js') as f:
        lines = f.read().splitlines()
        print(f'Writed {len(lines)} lines:')
        [print(f'{s[:50]}...    {s[-10:]}') for s in lines[:10]];
        print('...')
        
def boolean_collision_json(t):
    return collision_df(t.coords).to_json()


#if __name__ == '__main__':
    #pass
