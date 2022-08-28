#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from re import A
from typing import final
import dateutil.parser
import babel
import sys
import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(500))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(
        db.String(1))
    seeking_description = db.Column(db.String(500))


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.String(1))
    seeking_description = db.Column(db.String(500))

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"))
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"))
    start_time = db.Column(db.String(120))


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


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
    # TODO: replace with real venues data.
    locations = db.session.query(Venue.city, Venue.state).distinct()
    list_of_venues = db.session.query(
        Venue.id, Venue.name, Venue.city, Venue.state).all()
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    venue_dict = {}
    the_venues = []
    for a_venue in list_of_venues:
        # First - converting from tuples to dictionaries/objects
        if Venue.id:
            venue_dict["id"] = a_venue[Venue.id]
        if Venue.name:
            venue_dict["name"] = a_venue[Venue.name]
        if Venue.id:
            venue_dict["city"] = a_venue[Venue.city]
        if Venue.name:
            venue_dict["state"] = a_venue[Venue.state]

        # Second - query this venue's upcoming shows
        upcoming_shows = db.session.query(Venue.id).join(Show).filter(
            Venue.id == a_venue.id, Show.start_time > datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        num_upcoming_shows = upcoming_shows.count()

        # Third - add the num_upcoming_shows property
        venue_dict["num_upcoming_shows"] = num_upcoming_shows

        # Forth - send dictiony item to a list
        the_venues.append(venue_dict.copy())

    locations_dict = {}
    the_locations = []
    for location in locations:
        # First - converting from tuples to dictionaries/objects
        if Venue.city:
            locations_dict["city"] = location[Venue.city]
        if Venue.state:
            locations_dict["state"] = location[Venue.state]

        # Second - add the num_upcoming_shows property
        locations_dict["venues"] = []

        # Third - send dictiony item to a list
        the_locations.append(locations_dict.copy())

    # Finally combine data
    for a_location in the_locations:
        for a_venue in the_venues:
            if a_venue['city'] == a_location['city'] and a_venue['state'] == a_location['state']:
                a_location['venues'].append(a_venue)

    return render_template('pages/venues.html', areas=the_locations)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    venues = db.session.query(Venue.id, Venue.name).filter(
        Venue.name.ilike("%" + request.form.get('search_term') + "%"))

    no_of_venues = venues.count()
    response = {
        "count": no_of_venues,
        "data": venues,
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    selected_venue = Venue.query.get(venue_id)

    # Past shows
    past_shows = db.session.query(Artist.id, Artist.name,
                                  Artist.image_link, Show.start_time).join(Venue).join(Artist).filter(Venue.id == venue_id, Show.start_time < datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    past_shows_count = past_shows.count()

    # Upcoming shows
    upcoming_shows = db.session.query(Artist.id, Artist.name,
                                      Artist.image_link, Show.start_time).join(Venue).join(Artist).filter(Venue.id == venue_id, Show.start_time > datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    upcoming_shows_count = upcoming_shows.count()

    if selected_venue.genres[0] == "{" and selected_venue.genres[-1] == "}":
        the_genres = selected_venue.genres[1:-1].split(',')
    else:
        the_genres = list(selected_venue.genres)

    show_dict = {}
    the_past_shows = []
    the_upcoming_shows = []

    def convert_shows_from_tuple_to_list(tuple, list):
        for show in tuple:
            if Artist.id:
                show_dict["artist_id"] = show[Artist.id]
            if Artist.name:
                show_dict["artist_name"] = show[Artist.name]
            if Artist.image_link:
                show_dict["artist_image_link"] = show[Artist.image_link]
            if Show.start_time:
                show_dict["start_time"] = show[Show.start_time]
            list.append(show_dict.copy())

    convert_shows_from_tuple_to_list(past_shows, the_past_shows)
    convert_shows_from_tuple_to_list(upcoming_shows, the_upcoming_shows)

    setattr(selected_venue, "genres", the_genres)
    setattr(selected_venue, "past_shows", the_past_shows)
    setattr(selected_venue, "upcoming_shows", the_upcoming_shows)
    setattr(selected_venue, "past_shows_count", past_shows_count)
    setattr(selected_venue, "upcoming_shows_count", upcoming_shows_count)
    return render_template('pages/show_venue.html', venue=selected_venue)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        address = request.form.get('address')
        phone = request.form.get('phone')
        image_link = request.form.get('image_link')
        facebook_link = request.form.get('facebook_link')
        genres = request.form.getlist('genres')
        website = request.form.get('website_link')
        seeking_talent = request.form.get('seeking_talent')
        seeking_description = request.form.get('seeking_description')
        venue = Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, facebook_link=facebook_link,
                      genres=genres, website=website, seeking_talent=seeking_talent, seeking_description=seeking_description)
        db.session.add(venue)
        db.session.commit()
        # TODO: modify data to be the data object returned from db insertion

        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
        print(sys.exc_info())
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        Venue.query.filter(Venue.id == venue_id).delete()
        db.session.commit()
        flash('Venue deleted.')
    except:
        db.session.rollback()
        flash('An error occurred. Venue could not be deleted.')
        print(sys.exc_info())
    finally:
        db.session.close()
    return render_template('pages/home.html')

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

    #  Artists
    #  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    artists = db.session.query(Artist.id, Artist.name).filter(
        Artist.name.ilike("%" + request.form.get('search_term') + "%"))

    no_of_artists = artists.count()
    response = {
        "count": no_of_artists,
        "data": artists,
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    selected_artist = Artist.query.get(artist_id)
    # Past shows
    past_shows = db.session.query(Venue.id, Venue.name,
                                  Venue.image_link, Show.start_time).join(Artist).join(Venue).filter(Artist.id == artist_id, Show.start_time < datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    past_shows_count = past_shows.count()

    # Upcoming shows
    upcoming_shows = db.session.query(Venue.id, Venue.name,
                                      Venue.image_link, Show.start_time).join(Artist).join(Venue).filter(Artist.id == artist_id, Show.start_time > datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    upcoming_shows_count = upcoming_shows.count()

    show_dict = {}

    if selected_artist.genres[0] == "{" and selected_artist.genres[-1] == "}":
        the_genres = selected_artist.genres[1:-1].split(',')
    else:
        the_genres = list(selected_artist.genres)

    the_past_shows = []
    the_upcoming_shows = []

    def convert_shows_from_tuple_to_list(tuple, list):
        for show in tuple:
            if Venue.id:
                show_dict["venue_id"] = show[Venue.id]
            if Venue.name:
                show_dict["venue_name"] = show[Venue.name]
            if Venue.image_link:
                show_dict["venue_image_link"] = show[Venue.image_link]
            if Show.start_time:
                show_dict["start_time"] = show[Show.start_time]
            list.append(show_dict.copy())

    convert_shows_from_tuple_to_list(past_shows, the_past_shows)
    convert_shows_from_tuple_to_list(upcoming_shows, the_upcoming_shows)

    setattr(selected_artist, "genres", the_genres)
    setattr(selected_artist, "past_shows", the_past_shows)
    setattr(selected_artist, "upcoming_shows", the_upcoming_shows)
    setattr(selected_artist, "past_shows_count", past_shows_count)
    setattr(selected_artist, "upcoming_shows_count", upcoming_shows_count)
    return render_template('pages/show_artist.html', artist=selected_artist)

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    selected_artist = Artist.query.get(artist_id)
    # TODO: populate form with fields from artist with ID <artist_id>
    form.name.data = selected_artist.name
    form.city.data = selected_artist.city
    form.state.data = selected_artist.state
    form.phone.data = selected_artist.phone
    form.genres.data = selected_artist.genres
    form.facebook_link.data = selected_artist.facebook_link
    form.image_link.data = selected_artist.image_link
    form.website_link.data = selected_artist.website
    form.seeking_venue.data = selected_artist.seeking_venue
    form.seeking_description.data = selected_artist.seeking_description
    return render_template('forms/edit_artist.html', form=form, artist=selected_artist)


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form.get('facebook_link')
    artist.image_link = request.form.get('image_link')
    artist.website = request.form.get('website_link')
    artist.seeking_venue = request.form.get('seeking_venue')
    artist.seeking_description = request.form.get('seeking_description')
    db.session.commit()
    return redirect(url_for('show_artist', artist_id=artist_id))


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    selected_venue = Venue.query.get(venue_id)
    # TODO: populate form with values from venue with ID <venue_id>
    form.name.data = selected_venue.name
    form.genres.data = selected_venue.genres
    form.address.data = selected_venue.address
    form.city.data = selected_venue.city
    form.state.data = selected_venue.state
    form.phone.data = selected_venue.phone
    form.website_link.data = selected_venue.website
    form.facebook_link.data = selected_venue.facebook_link
    form.seeking_talent.data = selected_venue.seeking_talent
    form.seeking_description.data = selected_venue.seeking_description
    form.image_link.data = selected_venue.image_link
    return render_template('forms/edit_venue.html', form=form, venue=selected_venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.image_link = request.form.get('image_link')
    venue.facebook_link = request.form.get('facebook_link')
    venue.genres = request.form.getlist('genres')
    venue.website = request.form.get('website_link')
    venue.seeking_talent = request.form.get('seeking_talent')
    venue.seeking_description = request.form.get('seeking_description')
    db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        phone = request.form.get('phone')
        genres = request.form.getlist('genres')
        facebook_link = request.form.get('facebook_link')
        image_link = request.form.get('image_link')
        website = request.form.get('website_link')
        seeking_venue = request.form.get('seeking_venue')
        seeking_description = request.form.get('seeking_description')
        artist = Artist(name=name, city=city, state=state, phone=phone, image_link=image_link, facebook_link=facebook_link,
                        genres=genres, website=website, seeking_venue=seeking_venue, seeking_description=seeking_description)
        db.session.add(artist)
        db.session.commit()
        # TODO: modify data to be the data object returned from db insertion

        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
        print(sys.exc_info())
    finally:
        db.session.close()

        #  Shows
        #  ----------------------------------------------------------------


@ app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    shows = db.session.query(Venue.id, Venue.name, Artist.id, Artist.name,
                             Artist.image_link, Show.start_time).join(Artist).join(Venue).all()
    show_dict = {}
    data = []
    for show in shows:
        if Venue.id:
            show_dict["venue_id"] = show[Venue.id]
        if Venue.name:
            show_dict["venue_name"] = show[Venue.name]
        if Artist.id:
            show_dict["artist_id"] = show[Artist.id]
        if Artist.name:
            show_dict["artist_name"] = show[Artist.name]
        if Artist.image_link:
            show_dict["artist_image_link"] = show[Artist.image_link]
        if Show.start_time:
            show_dict["start_time"] = show[Show.start_time]
        data.append(show_dict.copy())

    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    try:
        artist_id = request.form.get('artist_id')
        venue_id = request.form.get('venue_id')
        start_time = request.form.get('start_time')
        show = Show(artist_id=artist_id, venue_id=venue_id,
                    start_time=start_time)
        db.session.add(show)
        db.session.commit()

        # on successful db insert, flash success
        flash('Show was successfully listed!')
        return render_template('pages/home.html')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
        print(sys.exc_info())
    finally:
        db.session.close()


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
