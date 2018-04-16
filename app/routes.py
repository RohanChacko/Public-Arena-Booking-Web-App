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
                return "Wrong password bitch"

            login_user(user, remember=form.remember_me.data)

            # next_page = request.args.get('next')								# causes a problem if i access acc directly using url edit and then try to login to another acc through ID, password. So changed it for now.
            next_page = 'index'
            # understand what it actually does xP
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('user', username=form.username.data)			#
            return redirect(url_for(next_page))

    elif reform.validate_on_submit():
        user = User(username=reform.Username2.data, email=reform.email.data)
        user.set_password(reform.Password2.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user', username=reform.Username2.data))
    else:
        return render_template('index.html', title='Sign Up', reform=reform, form=form)


@app.route('/user/<username>')
@login_required
def user(username=None):
    if current_user.username == username:
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
    start = int(time.mktime(time.strptime(
        date + ' ' + start_time, "%d/%m/%Y %H:%M")))
    session['start'] = start
    end = int(time.mktime(time.strptime(
        date + ' ' + end_time, "%d/%m/%Y %H:%M")))
    session['end'] = end
    available_venues = db.engine.execute("SELECT * FROM venues WHERE id NOT IN (SELECT venue_id FROM events WHERE (start_time <= :end_time AND end_time >= :start_time)) AND type == :type", {
                                         'start_time': start, 'end_time': end, 'type': type}).fetchall()
    # print(available_venues)
    return render_template('eventsecond.html', venues=available_venues)


@app.route('/user/<username>/confirm', methods=['POST'])
@login_required
def confirm(username=None):
    venue = request.form['venue']
    #name = request.form['name']
    #SAUJAS, WE DONT HAVE DESCRIPTION
    #type = request.form['eventype']
    db.engine.execute("INSERT INTO events (name, description, venue_id, creator_id, start_time, end_time, type) VALUES (:name, :description, :venue_id, :creator_id, :start_time, :end_time, :type)", {
                      'name': '', 'description': '', 'venue_id': venue, 'creator_id': 0, 'start_time': session['start'], 'end_time': session['end'], 'type': 0})
    venue_details = db.engine.execute(
        "SELECT * FROM venues WHERE id==:id", {'id': venue}).fetchall()
    db.session.commit()
    #print(db.engine.execute("SELECT * FROM events").fetchall())
    date = time.strftime("%d/%m/%Y", time.gmtime(session['start']))
    start = time.strftime("%H:%M", time.gmtime(session['start']))
    end = time.strftime("%H:%M", time.gmtime(session['end']))
    event = {'date': date, 'start': start, 'end': end}
    print(event, venue_details)
    return render_template('confirm.html', event=event, venue=venue_details[0])


@app.route('/user/<username>/events', methods=['GET'])
@login_required
def events(username=None):
    id = db.engine.execute("SELECT id FROM user WHERE username == :username", {
                           'username': username}).fetchall()[0][0]
    # print(id)
    public_events = db.engine.execute(
        "SELECT * FROM events WHERE type == 0").fetchall()
    private_events = db.engine.execute(
        "SELECT * FROM events WHERE id IN (SELECT event_id FROM invites WHERE (invitee_id == :id OR inviter_id == :id))", {'id': id}).fetchall()
    return render_template('events.html', events_list=public_events + private_events)


@app.route('/user/<username>/invite/<int:event_id>', methods=['GET', 'POST'])
@login_required
def invite(username=None, event_id=None):
    print(db.engine.execute("SELECT * FROM user").fetchall())
    if request.method == 'GET':
        invite = db.engine.execute(
            "SELECT * FROM invites WHERE event_id == :event_id", {'event_id': event_id})
        return render_template('invite.html', invite=invite, event=event_id)
    elif request.method == 'POST':
        invitee = request.form['invitee']
        inviter_id = db.engine.execute("SELECT id FROM user WHERE username == :username", {
                                       'username': username}).fetchall()[0][0]
        invitee_id = db.engine.execute("SELECT id FROM user WHERE username == :username", {
                                       'username': invitee}).fetchall()[0][0]
        if inviter_id == invitee_id:
            invite = db.engine.execute("SELECT username FROM user WHERE id IN (SELECT invitee_id FROM invites WHERE event_id == :event_id)", {
                                       'event_id': event_id}).fetchall()
            return render_template('invite.html', invite=invite, event=event_id)
        db.engine.execute("INSERT INTO invites (inviter_id, invitee_id, event_id, status) VALUES (:inviter_id, :invitee_id, :event_id, 0)", {
                          'inviter_id': inviter_id, 'invitee_id': invitee_id, 'event_id': event_id})
        db.session.commit()
        invite = db.engine.execute("SELECT username FROM user WHERE id IN (SELECT invitee_id FROM invites WHERE event_id == :event_id)", {
                                   'event_id': event_id}).fetchall()
        return render_template('invite.html', invite=invite, event=event_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.debug()
    app.run(debug=True)
