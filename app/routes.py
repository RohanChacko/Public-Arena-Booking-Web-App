from flask import Flask, render_template, redirect, request, flash, url_for
from app import app, db
from app.forms import LoginForm, SignUp
from app.models import User, Venues, Events, Invites
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

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
	print(request.data)
	# type = data['type'] #get type from request
	# start_time = data['start_time'] #get starttime from request
	# end_time = data['end_time'] #get endtime from request
	# available_venues = db.execute("SELECT venues.* FROM venues JOIN events ON venues.id == events.venue_id WHERE venues.type == :type AND (events.start_time > :endtime OR events.end_time < :start_time)", {'start_time':start_time, 'end_time':end_time}).fetchall()
	return render_template('eventsecond.html')#, venues=available_venues)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

if __name__ == '__main__':
	app.debug()
	app.run (debug = True)
