# cayuman_flask web application
School workshops inscription web form for students enrollment.

## Flask, pandas and odfpy
Needs python flask, pandas and odfpy modules in order to read input data libreoffice table.

## Jupyter notebook Quick testing
See [`quick_testing.ipynb`](quick_testing.ipynb) jupyter notebook to understand and test some code logic. Some of these code is used in [`pdbase.py`](pdbase.py) to parse excel data and in [`flask_app.py`](flask_app.py) to handle the url request and render the form.

## Launch

Launch the local web server with `flask run`.
```bash
export FLASK_APP=flask_app.py
flask run
```
View the interactive web form at `http://localhost:5000/<cycle>` where cycle is one of the followings:

        - ulmos
        - canelos
        - manios
        - coihues
        - avellanos
Example URL : [http://localhost:5000/ulmos](http://localhost:5000/ulmos)
