#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from flask import Flask, redirect, render_template, request, url_for
from myforms import create_switched_enrollment_class
import pdbase

app = Flask(__name__)
app.secret_key = b'r\x191\x9en\x08T\xb15DX<\x0c:\x1dj'
pdbase.create_inscription_table(pdbase.ws_table(nan_names='(No definido)'))

def week_schedule(idx, t):
    by_coords = {(a,b): [] for a in range(len(pdbase.TIMES_LIST))
                         for b in range(len(pdbase.DAYS_LIST))}
    for i in idx:
            for coord in t.loc[i,'coords']:
                by_coords[coord].append(t.loc[i,'name'])
    return { k: (v[0] if len(v)>0 else '')
             for k, v in by_coords.items() }

def week_table_rows(d):
    return [[d[(a,b)] for b in range(len(pdbase.DAYS_LIST))]
                          for a in range(len(pdbase.TIMES_LIST))]

def is_valid_schedule(d):
    return '' not in d.values()


@app.route('/horario/', methods=['GET'])
def table_view():
    cycle = request.args['cycle']
    sname = request.args['sname']
    idx_str = request.args['idx_str']
    t = pdbase.ws_table(nan_names='(No definido)')
    idx = []
    if idx_str != '':
        idx = [int(s) for s in request.args['idx_str'].split(' ')]
    ws_schedule = week_schedule(idx, t)
    rows = week_table_rows(ws_schedule)
    headers = pdbase.TIMES_LIST
    days = pdbase.DAYS_LIST
    if is_valid_schedule(ws_schedule):
        print(f"#############Storing:{idx}")
        pdbase.insert_to_dbase(sname, cycle, idx, t)
    else:
        print(f'#############Should flash an invalid message')
    return render_template('week_table.html',
                           se_rows=zip(headers, rows),
                           days=days)

@app.route('/<period>/<ciclo>/<sname>', methods=['GET', 'POST'])
def enrollment(period, ciclo, sname):
    cycle_name = {
        'ulmos': 'ulmos',
        'canelos': 'canelos y manios',
        'manios': 'canelos y manios',
        'coihues': 'coihues y avellanos',
        'avellanos': 'coihues y avellanos'}
    #Pendig fix: change this hidden return.
    #Better wrong ciclo and period handling.
    if ciclo not in cycle_name: return ''
    if period not in '12345': return ''
    #Create table with every request in order to see updated excel data
    #without flask server reboot
    ws_table = pdbase.ws_table(nan_names='(No definido)')
    ws_table.loc[:,'applied'] = pdbase.read_from_dbase(ws_table)
    t = ws_table[(ws_table.period == int(period))&
                 (ws_table.cycle == cycle_name[ciclo])]
    t = pdbase.sort_by_day_time(t)
    MyForm = create_switched_enrollment_class(
        t,
        pdbase.TIMES_LIST,
        pdbase.DAYS_LIST)
    form = MyForm()
    
    #Grouping form fields in form.groups dict.
    #Dict values are two keys dicts with inputs labels and texts that don't use inputs.
    #form.groups
    #{'<Day and time str>': {'inputs': [<input label>, ...] , 'texts': [<text>, ...]} }
    form.daytime_grouping()
    if form.validate_on_submit():
        #Make selected workshops index string
        idx = [ form.name_idx(k) for k, v in form.data.items() 
                if k != 'csrf_token' and v ]
        idx_str = ' '.join([str(i) for i in idx])
        return redirect(url_for('table_view',
                                cycle=cycle_name[ciclo],
                                sname=sname,
                                idx_str=idx_str))
    return render_template('switch_form.html',
                           form=form,
                           bool_json = pdbase.boolean_collision_json(t))

#if __name__ == '__main__':
    #pass
