# Public Arena Booking Web Application

 Web App made using Flask and Materialize CSS with Jinja2 templating

## Install dependencies
` pip install flask-sqlalchemy `  
` pip install flask-migrate `  
` pip install flask-wtf `  
` pip install flask-login `

## Setting up Web App
` flask run `
## Directory Structure

```
├── app
│   ├── forms.py
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── static
│   │   ├── images
│   │   │   ├── profilepicture1.jpg
│   │   │   ├── profilepicture2.jpeg
│   │   │   └── profilepicture3.jpg
│   │   ├── materialize.js
│   │   ├── materialize.min.js
│   │   └── styles
│   │       ├── css
│   │       ├── materialize.css
│   │       ├── materialize.min.css
│   │       └── style.css
│   ├── templates
│   │   ├── base.html
│   │   ├── confirm.html
│   │   ├── eventsecond.html
│   │   ├── events.html
│   │   ├── form.html
│   │   ├── index.html
│   │   ├── invite.html
│   │   ├── loggedin.html
│   │   └── searchres.html
│   └── utility.py
├── app.db
├── config.py
└── documents
    ├── Design Doc
    └── Technical Doc
```
