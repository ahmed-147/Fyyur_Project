#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from flask_migrate import Migrate
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
# DONE: connect to a local postgresql database

# ----------------------Migration--------------------
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):

  __tablename__ = 'venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String()))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean)
  seeking_description = db.Column(db.String(500))
  shows = db.relationship('Show', backref="venue", lazy=True )

  
  
    # DONE: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref="artist", lazy=True)

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__= 'show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)



# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  td = datetime.now()
  all_areas = Venue.query.all()
  states = []
  city = []
  data = []
  
  
  for area in all_areas:
    if area.state not in states  :
      area_venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
      venue_data = []
      for venue in area_venues:
        num_show = 0
        showinid = Show.query.filter_by(venue_id=venue.id).all()
        for n in showinid:
          if n.start_time > td:
            num_show += 1

        # print(num_show)
        venue_data.append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": num_show 
        })
      data.append({
        "city": area.city,
        "state": area.state, 
        "venues": venue_data
      })
      states.append(area.state)
      city.append(area.city)
    elif area.city not in city :
      area_venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
      venue_data = []
      for venue in area_venues:
        num_show = 0
        showinid = Show.query.filter_by(venue_id=venue.id).all()
        for n in showinid:
          if n.start_time > td:
            num_show += 1

        # print(num_show)
        venue_data.append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": num_show 
        })
      data.append({
        "city": area.city,
        "state": area.state, 
        "venues": venue_data
      })
      states.append(area.state)
      city.append(area.city)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  da = []
  td = datetime.now()
  slic = '%'+request.form['search_term']+'%'
  count = Venue.query.filter(Venue.name.like(slic)).count()
  all_v = Venue.query.filter(Venue.name.like(slic)).all()
  

  for v in all_v:

    incom_sh_c = 0
    showinid = Show.query.filter_by(venue_id=v.id).all()
   
    for n in showinid:
      if n.start_time > td:
        incom_sh_c += 1
    
    da.append({
      "id": v.id,
      "name": v.name,
      "num_upcoming_shows": incom_sh_c,
    })

  response={
    "count": count,
    "data": da
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id

  td = datetime.now()
  all_v = Venue.query.filter_by(id=venue_id).all()
  past_show = []
  incom_show = []
  da = []

  for v in all_v:
    incom_sh_c = 0
    past_show_c= 0

    showinid = Show.query.filter_by(venue_id=v.id).all()
    for n in showinid:
      if n.start_time > td:
        incom_show.append({
        "artist_id": n.artist_id,
        "artist_name": n.artist.name,
        "artist_image_link": n.artist.image_link,
        "start_time": n.start_time.strftime('%Y-%m-%dT%H:%M:%SZ') 
        })

        incom_sh_c += 1
      else:
        past_show.append({
        "artist_id": n.artist_id,
        "artist_name": n.artist.name,
        "artist_image_link": n.artist.image_link,
        "start_time": n.start_time.strftime('%Y-%m-%dT%H:%M:%SZ') 
        })
        past_show_c+= 1
    
    da.append({
    "id": v.id,
    "name": v.name,
    "genres": v.genres,
    "address": v.address,
    "city": v.city,
    "state": v.state,
    "phone": v.phone,
    "website": v.website,
    "facebook_link": v.facebook_link,
    "seeking_talent": v.seeking_talent,
    "seeking_description": v.seeking_description,
    "image_link": v.image_link,
    "past_shows": past_show,
    "upcoming_shows": incom_show ,
    "past_shows_count": past_show_c,
    "upcoming_shows_count": incom_sh_c })
  
  data = list(filter(lambda d: d['id'] == venue_id, da ))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  error = False
 
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist("genres")
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = request.form['website']
    print(request.form['seeking_talent'])
    if request.form['seeking_talent'] == 'True':
      se_tal=True
    elif request.form['seeking_talent']  == 'False':
      se_tal=False
    seeking_description = request.form['seeking_description']

    new_ven = Venue(name=name,city=city,state=state,address=address,phone=phone,genres=genres,image_link=image_link,facebook_link=facebook_link,website=website,seeking_talent=se_tal,seeking_description=seeking_description)
    print(new_ven)
    db.session.add(new_ven)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Venue ' + request.form['name']+ ' was successfully listed!')
  return render_template('pages/home.html')
  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<int:venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    print('deleted')
  except:
    print('error !')
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database

  # select all Artists form the database 
  artists = Artist.query.all()
  data = []
  for artist in artists:
      ar = {"id" : artist.id , "name":artist.name}
      data.append(ar)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  da = []
  td = datetime.now()
  slic = '%'+request.form['search_term']+'%'
  count = Artist.query.filter(Artist.name.ilike(slic)).count()
  all_a = Artist.query.filter(Artist.name.ilike(slic)).all()
  

  for a in all_a:

    incom_sh_c = 0
    showinid = Show.query.filter_by(artist_id=a.id).all()
   
    for n in showinid:
      if n.start_time > td:
        incom_sh_c += 1
    
    da.append({
      "id": a.id,
      "name": a.name,
      "num_upcoming_shows": incom_sh_c,
    })


  response={
    "count": count,
    "data": da
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  
  td = datetime.now()
  all_a = Artist.query.filter_by(id=artist_id).all()
  past_show = []
  incom_show = []
  da = []

  for a in all_a:
    incom_sh_c = 0
    past_show_c= 0

    showinid = Show.query.filter_by(artist_id=a.id).all()
    for n in showinid:
      if n.start_time > td:
        incom_show.append({
          "venue_id": n.venue_id,
          "venue_name": n.venue.name,
          "venue_image_link": n.venue.image_link,
          "start_time": n.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        })

        incom_sh_c += 1
      else:
        past_show.append({
          "venue_id": n.venue_id,
          "venue_name": n.venue.name,
          "venue_image_link": n.venue.image_link,
          "start_time": n.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        })
        past_show_c += 1
    
    da.append({
      "id": a.id,
      "name": a.name,
      "genres": a.genres,
      "city": a.city,
      "state": a.state,
      "phone": a.phone,
      "website": a.website,
      "facebook_link": a.facebook_link,
      "seeking_venue": a.seeking_venue,
      "seeking_description": a.seeking_description,
      "image_link": a.image_link,
      "past_shows": past_show,
      "upcoming_shows": incom_show,
      "past_shows_count": past_show_c,
      "upcoming_shows_count": incom_sh_c })

  data = list(filter(lambda d: d['id'] == artist_id, da))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  art = Artist.query.filter_by(id=artist_id).one()
  artist={
    "id": art.id,
    "name": art.name,
    "genres": art.genres,
    "city": art.city,
    "state": art.state,
    "phone": art.phone,
    "website": art.website,
    "facebook_link": art.facebook_link,
    "seeking_venue": art.seeking_venue,
    "seeking_description": art.seeking_description,
    "image_link": art.image_link
  }
  # DONE populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  
  art = Artist.query.filter_by(id=artist_id).one()
  error = False
 
  try:
    art.name = request.form['name']
    art.city = request.form['city']
    art.state = request.form['state']
    art.phone = request.form['phone']
    art.genres = request.form.getlist("genres")
    art.image_link = request.form['image_link']
    art.facebook_link = request.form['facebook_link']
    art.website = request.form['website']
    if request.form['seeking_venue'] == 'True':
      art.seeking_venue=True
    elif request.form['seeking_venue']  == 'False':
      art.seeking_venue=False
    art.seeking_description = request.form['seeking_description']

    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    print('error')
  else:
    print('successfully listed!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  ven = Venue.query.filter_by(id=venue_id).one()
  venue={
    "id": ven.id,
    "name": ven.name,
    "genres": ven.genres,
    "address":ven.address,
    "city": ven.city,
    "state": ven.state,
    "phone": ven.phone,
    "website": ven.website,
    "facebook_link": ven.facebook_link,
    "seeking_talent": ven.seeking_talent,
    "seeking_description": ven.seeking_description,
    "image_link": ven.image_link
  }
  # DONE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  ven = Venue.query.filter_by(id=venue_id).one()
  error = False
 
  try:
    ven.name = request.form['name']
    ven.address= request.form['address'],
    ven.city = request.form['city']
    ven.state = request.form['state']
    ven.phone = request.form['phone']
    ven.genres = request.form.getlist("genres")
    ven.image_link = request.form['image_link']
    ven.facebook_link = request.form['facebook_link']
    ven.website = request.form['website']
    if request.form['seeking_talent'] == 'True':
      ven.seeking_talent=True
    elif request.form['seeking_talent']  == 'False':
      ven.seeking_talent=False
    ven.seeking_description = request.form['seeking_description']

    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    print('error')
  else:
    print('successfully listed!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  error = False
 
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist("genres")
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = request.form['website']
    if request.form['seeking_venue'] == 'True':
      se_ven=True
    elif request.form['seeking_venue']  == 'False':
      se_ven=False
    seeking_description = request.form['seeking_description']

    new_art = Artist(name=name,city=city,state=state,phone=phone,genres=genres,facebook_link=facebook_link,image_link=image_link,website=website,seeking_venue=se_ven,seeking_description=seeking_description)
    db.session.add(new_art)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  today = datetime.now()
  print (today)
  da = []
  sho = Show.query.all()
  for s in sho:
    if s.start_time > today:
      da.append({
        'venue_id': s.venue_id ,
        'venue_name': s.venue.name ,
        'artist_id': s.artist_id ,
        'artist_name': s.artist.name ,
        'artist_image_link': s.artist.image_link ,
        'start_time':  s.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        
      })

  
  return render_template('pages/shows.html', shows=da)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE: insert form data as a new Show record in the db, instead
  error = False
  try:
    artist_id = int(request.form['artist_id'])
    venue_id = int(request.form['venue_id'])
    start_time = request.form['start_time']
    
    new_show = Show(artist_id=artist_id,venue_id=venue_id,start_time=start_time)
    
    db.session.add(new_show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')
  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
