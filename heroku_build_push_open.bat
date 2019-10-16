heroku login
heroku container:login
heroku container:push web --app cloud-photo-gallery
heroku container:release web --app cloud-photo-gallery
ECHO 'press any key to open heroku'
PAUSE
heroku open --app cloud-photo-gallery
PAUSE