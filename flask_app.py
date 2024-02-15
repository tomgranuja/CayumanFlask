#!/usr/bin/env python3
#-*- coding:utf-8 -*-

# import datetime
# import uuid
# from flask import Flask, render_template, flash, redirect, url_for, request
from myforms import create_radio_enrollment_class, create_switched_enrollment_class

from flask import Flask, render_template
import pdbase

days_list = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
times_list = [('10:15', '11:15'), ('12:30', '13:30')]

app = Flask(__name__)
app.secret_key = b'r\x191\x9en\x08T\xb15DX<\x0c:\x1dj'

def week_schedule(d={}):
    new = {(a,b): '' for a in range(len(times_list))
                         for b in range(len(days_list))}
    return {**new, **d}

def week_table_rows(d):
    return [[d[(a,b)] for b in range(len(days_list))]
                          for a in range(len(times_list))]

@app.route('/horario')
def table_view():
    d = week_schedule(workshop_times)
    rows = week_table_rows(d)
    headers = times_list
    return render_template('week_table.html',
                           se_rows=zip(headers, rows),
                           days=days_list)

@app.route('/<ciclo>', methods=['GET', 'POST'])
def enrollment(ciclo):
    cycle_name = {
        'ulmos': 'ulmos',
        'canelos': 'canelos y manios',
        'manios': 'canelos y manios',
        'coihues': 'coihues y avellanos',
        'avellanos': 'coihues y avellanos'}
    #Pendig fix: change this hidden return.
    #Better wrong ciclo handling.
    if ciclo not in cycle_name: return ''
    
    #Create table with every request in order to see updated excel data
    #without flask server reboot
    ws_table = pdbase.ws_table()
    t = ws_table[ws_table.cycle == cycle_name[ciclo]]
    t = pdbase.sort_by_day_time(t)
    MyForm = create_switched_enrollment_class(
        t,
        times_list,
        days_list)
    form = MyForm()
    
    #Grouping form fields in form.groups dict.
    #Dict values are two keys dicts with inputs labels and texts that don't use inputs.
    #form.groups
    #{'<Day and time str>': {'inputs': [<input label>, ...] , 'texts': [<text>, ...]} }
    form.daytime_grouping()
    
    if form.validate_on_submit():
        #Make week shedule table rows
        workshop_times = {(a,b): [] for a in range(len(times_list))
                         for b in range(len(days_list))}
        idx = [ form.name_idx(k) for k, v in form.data.items() 
                 if k != 'csrf_token' and v ]
        for i in idx:
            for coord in t.loc[i,'coords']:
                workshop_times[coord].append(t.loc[i,'name'])
        all_week = {
            k: (v[0] if len(v)>0 else '')
            for k, v in workshop_times.items()
        } 
        rows = week_table_rows(all_week)
        headers = times_list
        return render_template('week_table.html',
                           se_rows=zip(headers, rows),
                           days=days_list,
                           )      
    return render_template('switch_form.html',
                           form=form,
                           bool_json = pdbase.boolean_collision_json(cycle_name[ciclo]))

#if __name__ == '__main__':
    #pass
