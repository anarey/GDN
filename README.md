GDN: Generic Developers Network web application
===============================================

Requirements
------------
* `Django 1.3`
* `gobject-introspection`
* `libgirepository1.0-dev`
* `libgtk-3-dev`

In Ubuntu:
`apt-get install gobject-introspection libgirepository1.0-dev libgtk-3-dev`

How to Install:
---------------

* Clone to repo:
`git clone https://github.com/aruiz/GDN.git`

* Config the database. By defaults, the database is set in `/mnt/development.sqlite`

 * `$sudo mkfs.ext2 /dev/ram0 20480`
 * `$sudo mount /dev/ram0 /mnt/`
 * `$sudo chown user:user /mnt/`

* It necesary run the commnand to created the database:
`$python manager.py syncdb`

* Running the app.
python manager.py runserver

* Generar la informacion en la base de datos.
python manage.py parsegir


URL: Where is the app? 
----------------------
 
* http://localhost:8000/api
* http://localhost:8000/admin


project structure
-----------------
$ls GND/
```
api/
  admin.py
  models.py
  storage.py
  tests.py
  urls.py
  views.py
AUTHORS
COPYING
manage.py
README.mb
settings.py
templates/
  base.html
  overview.html
urls.py
```
