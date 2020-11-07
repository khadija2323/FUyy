
#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    area_id = db.Column(db.Integer, db.ForeignKey('Area.id'), nullable=False)
    genres = db.Column(db.String(120))
    website = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    past_shows_count = db.Column(db.Integer)
    past_shows = db.relationship('PastShow', backref='venue')
    upcoming_shows_count = db.Column(db.Integer)
    upcoming_shows = db.relationship('UpcomingShow', backref='venue')

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    website = db.Column(db.String)
    seeking_venues = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    upcoming_shows_count = db.Column(db.Integer)
    upcoming_shows = db.relationship('UpcomingShow', backref='artist')
    past_shows_count = db.Column(db.Integer)
    past_shows = db.relationship('PastShow', backref='artist')

class UpcomingShow(db.Model):
    __tablename__ = 'upcomingshows'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime)

class PastShows(db.Model):
    __tablename__ = 'pastshows'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime)

class Area(db.Model):
    __tablename__ = 'areas'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    venues = db.relationship('Venue', backref='Area')


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
    data = Area.query.all()
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
    search = request.form.get('search_term', '')
    data = Venue.query.filter(func.lower(Venue.name).contains(func.lower(search))).all()
    response = {
        "count": len(data),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=search)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    data = Venue.query.get(venue_id)
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    area = Area.query.filter(Area.city == request.form['city']).filter(Area.state == request.form['state']).first()
    stored = True

    if not area:
        area = Area(
            city=request.form['city'],
            state=request.form['state']
        )

        try:
            db.session.add(area)
            db.session.flush()
        except:
            db.session.rollback()
            stored = False
        finally:
            db.session.close()

    if stored:
        venue = Venue(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            address=request.form['address'],
            phone=request.form['phone'],
            image_link='',
            facebook_link='',
            area_id=area.id,
            genres='',
            website='',
            seeking_talent=True,
            seeking_description='',
            upcoming_shows_count=0,
            past_shows_count=0,
        )

        try:
            db.session.add(venue)
            db.session.commit()
        except:
            db.session.rollback()
            stored = False
        finally:
            db.session.close()

    if stored:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
        flash('An error occurred. Venue ' + request.form['name'] + 'could not be listed.')

    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    venue = Venue.query.get(venue_id)
    deleted = True

    try:
        venue.delete()
        db.session.commit()
    except:
        db.session.rollback()
        deleted = False
    finally:
        db.session.close()

    if deleted:
        flash('Venue was successfully deleted!')
    else:
        flash('An error occurred. Venue could not be deleted.')

    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    user_input = request.form.get('search_term', '')
    response = Artist.query.filter(func.lower(Artist.name).contains(func.lower(user_input))).all()
    
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    data = Artist.query.get(artist_id)
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    updated = True

    try:
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        db.session.commit()
    except:
        db.session.rollback()
        updated = False
    finally:
        db.session.close()

    if updated:
        flash('Artist ' + artist.name + '\'s data was successfully updated')
    else:
        flash('An error occurred. Artist ' + artist.name + '\'s data could not be updated.')

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    updated = True

    try:
        venue.name = request.form['name']
        venue.phone = request.form['phone']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        
        db.session.commit()
    except:
        db.session.rollback()
        updated = False
    finally:
        db.session.close()

    if updated:
        flash('Venue ' + venue.name + '\'s data was successfully updated')
    else:
        flash('An error occurred. Venue ' + venue.name + '\'s data could not be updated.')

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    artist = Artist(
        name=request.form['name'],
        city=request.form['city'],
        state=request.form['state'],
        phone=request.form['phone'],
        genres='',
        image_link='',
        facebook_link='',
        website='',
        seeking_venues=True,
        seeking_description='',
        upcoming_shows_count=0,
        past_shows_count=0,
    )
    failed = False

    try:
        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
        failed = True
    finally:
        db.session.close()

    if not failed:
        flash('Artist was successfully listed!')
    else:
        flash('An error occurred. Artist could not be listed.')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = db.session.query(UpcomingShow, Venue, Artist).select_from(UpcomingShow).join(Venue).join(Artist).all()
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    show = UpcomingShow(
        venue_id=request.form['venue_id'],
        artist_id=request.form['artist_id'],
        start_time=request.form['start_time']
    )

    venue = Venue.query.get(request.form['venue_id'])
    artist = Artist.query.get(request.form['artist_id'])
    stored = True

    try:
        artist.upcoming_shows_count += 1
        venue.upcoming_shows_count += 1
        db.session.add(show)
        db.session.commit()
    except:
        db.session.rollback()
        stored = False
    finally:
        db.session.close()

    if stored:
        flash('Show was successfully listed!')
    else:
        flash('An error occurred. Show could not be listed!')

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
