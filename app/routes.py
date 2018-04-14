from flask import Flask, render_template, redirect, request, flash, url_for, session
from app import app, db
from app.forms import LoginForm, SignUp
from app.models import User, Venues, Events, Invites
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
import time
from sqlalchemy import and_

@app.route('/', methods=['GET', 'POST'])
def index():

	if current_user.is_authenticated:
		return redirect(url_for('user', username=current_user.username))

	form = LoginForm()
	reform = SignUp()

	if form.submitlogin.data == 1 and reform.submitsignup.data == 0:
		if form.validate_on_submit():
			user = User.query.filter_by(username=form.username.data).first()
			if user is None or not user.check_password(form.password.data):
				flash('Invalid username or password')
				return "Wrong password bitch"

			login_user(user, remember=form.remember_me.data)

			#next_page = request.args.get('next')								# causes a problem if i access acc directly using url edit and then try to login to another acc through ID, password. So changed it for now.
			next_page = 'index'
			if not next_page or url_parse(next_page).netloc != '':				# understand what it actually does xP
				next_page = url_for('user',username=form.username.data)			#
			return redirect(url_for(next_page))

	elif reform.validate_on_submit():
		user = User(username=reform.username.data, email=reform.email.data)
		user.set_password(reform.password.data)
		db.session.add(user)
		db.session.commit()
		flash('You are in the presence of the IT God now...')				# which part of the page does it actually flash?
		return redirect(url_for('user',username=reform.username.data))

	return render_template('index.html', title='Sign Up', reform=reform, form=form)



@app.route('/user/<username>')
@login_required
def user(username = None):
	if current_user.username == username:
		#user = User.query.filter_by(username=username).first_or_404()
		#books = [{'venue': user, 'timestamp': '23-01-1999'},{'venue': user, 'timestamp': '13-04-1999'}]
		types = Venues.query.with_entities(Venues.type).distinct().all()
		types_list = [i[0] for i in types]
		return render_template('loggedin.html', types=types_list)
	else:
		return redirect(url_for('index'))

@app.route('/user/<username>/event2', methods=['POST'])
@login_required
def eventsecond(username=None):
	type = request.form['select']
	session['type'] = type
	date = request.form['date']
	start_time = request.form['start_time']
	end_time = request.form['end_time']
	#print(type, date, start_time, end_time)
	start = int(time.mktime(time.strptime(date + ' ' + start_time, "%d/%m/%Y %H:%M")))
	session['start'] = start
	end = int(time.mktime(time.strptime(date + ' ' + end_time, "%d/%m/%Y %H:%M")))
	session['end'] = end
	available_venues = db.engine.execute("SELECT * FROM venues WHERE id NOT IN (SELECT venue_id FROM events WHERE (start_time <= :end_time AND end_time >= :start_time)) AND type == :type", {'start_time':start, 'end_time':end, 'type':type}).fetchall()
	#print(available_venues)
	return render_template('eventsecond.html', venues=available_venues)

@app.route('/user/<username>/confirm', methods=['POST'])
@login_required
def confirm(username=None):
	venue = request.form['venue']
	db.engine.execute("INSERT INTO events (name, description, venue_id, creator_id, start_time, end_time, type) VALUES (:name, :description, :venue_id, :creator_id, :start_time, :end_time, :type)", {'name':'', 'description':'', 'venue_id':venue, 'creator_id':0, 'start_time':session['start'], 'end_time':session['end'], 'type':0})
	venue_details = db.engine.execute("SELECT * FROM venues WHERE id==:id", {'id':venue}).fetchall()
	db.session.commit()
	#print(db.engine.execute("SELECT * FROM events").fetchall())
	date = time.strftime("%d/%m/%Y", time.gmtime(session['start']))
	start = time.strftime("%H:%M", time.gmtime(session['start']))
	end = time.strftime("%H:%M", time.gmtime(session['end']))
	event = {'date': date, 'start': start, 'end': end}
	print(event, venue_details)
	return render_template('confirm.html', event=event, venue=venue_details[0])

@app.route('/user/<username>/events',methods=['GET'])
@login_required
def events(username=None):
	return render_template('events.html')


@app.route('/user/<username>/invite',methods=['GET','POST'])
@login_required
def invite(username=None):

	return render_template('invite.html')

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

if __name__ == '__main__':
	app.debug()
	app.run (debug = True)
