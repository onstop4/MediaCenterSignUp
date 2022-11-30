# Media Center Sign-Up System
This is a web application I designed to keep track of attendance for the media center at [Holy Cross High School](https://holycrosshs.org/).
Students can sign up to attend the media center during specific class periods, and faculty can set the maximum number of students for each period. Faculty can also view a list of students who signed up and mark whether or not they are actually present.

This system was built using Django. It is comprised of a general "signup" app and an inner "faculty" app. (This separation was created when I thought that the faculty-side of the web app might contain special models. This turned out not to be the case.) Users must log in with their Holy Cross Google account in order to access the app's functionality. The frontend uses Bootstrap to style the pages. One of the faculty views is comprised of a Vue.js app that communicates with a private REST API. This allows a list of students who signed up to be presented/filtered without requiring the page to be refreshed.

Originally, the web app was intended to be deployed on Heroku and use the Celery Beat task scheduler to remove old signups after a specific period of time. Even though this is no longer the case, the Celery-related code still exists. It has been modified so that Celery does not have to be installed to run the app.
