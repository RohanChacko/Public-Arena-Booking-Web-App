from flask import Flask, render_template, redirect, request, flash, url_for, session
from app import app, db
from app.utility import *
from app.forms import LoginForm, SignUp
from app.models import User, Venues, Events, Invites
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
import time
from sqlalchemy import and_
import datetime


@app.route('/', methods=['GET', 'POST'])
def index():

    if current_user.is_authenticated:
        return redirect(url_for('user', username=current_user.username))

    form = LoginForm()
    reform = SignUp()

    public_events = db.engine.execute("SELECT * FROM events WHERE type == 0").fetchall()
    events_list = list()
    for event in public_events:
        venue_name = db.engine.execute("SELECT name FROM venues WHERE id == :id", {'id': event[3]}).fetchall()[0][0]
        try:
            creator = db.engine.execute("SELECT username FROM user WHERE id == :id", {'id': event[4]}).fetchall()[0][0]
        except:
            creator = ''
        date = time.strftime("%d/%m/%Y", time.gmtime(event[5]))
        start = time.strftime("%H:%M", time.gmtime(event[5]))
        end = time.strftime("%H:%M", time.gmtime(event[6]))
        events_list.append({'name': event[1], 'description': event[2], 'date': date, 'start_time': start, 'end_time': end, 'venue': venue_name, 'creator': creator})


    if form.submitlogin.data == 1 and reform.submitsignup.data == 0:
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                return render_template('index.html',failmsg=1,reform=reform, form=form, events=events_list)

            login_user(user, remember=form.remember_me.data)

            # next_page = request.args.get('next')                                # causes a problem if i access acc directly using url edit and then try to login to another acc through ID, password. So changed it for now.
            next_page = 'index'
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('user', username=form.username.data)
            return redirect(url_for(next_page))

    elif reform.validate_on_submit():
        user = User(username=reform.Username2.data, email=reform.email.data)
        user.set_password(reform.Password2.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user', username=reform.Username2.data))
    else:
        return render_template('index.html',failmsg=0,title='Sign Up', reform=reform, form=form, events=events_list)


@app.route('/user/<username>')
@login_required
def user(username=None):
    if current_user.username == username:
        types = Venues.query.with_entities(Venues.type).distinct().all()
        types_list = [i[0] for i in types]
        return render_template('loggedin.html', types=types_list)
    else:
        return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search():
    searchstring = request.form['searchstring']
    pattern = '%' + searchstring + '%'
    events = db.engine.execute("SELECT * FROM events WHERE name LIKE :pattern OR hash LIKE :pattern OR creator_id IN (SELECT id FROM user WHERE username LIKE :pattern)", {'pattern': pattern})
    return render_template('events.html', events_list=events)



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


@app.route('/user/<username>/confirm', methods=['POST', 'GET'])
@login_required
def confirm(username=None):
    if request.method == 'GET':
        event_id = request.args['event_id']
        event = db.engine.execute("SELECT * FROM events WHERE id == :id", {'id': event_id}).fetchone()
        venue = event[3]
        venue_details = db.engine.execute(
            "SELECT * FROM venues WHERE id==:id", {'id': venue}).fetchone()
        return render_template('confirm.html', event_id=event_id, event=get_event_data_single(event), venue=venue_details)
    elif request.method == 'POST':
        venue = request.form['venue']
        name = request.form['name']
        description = request.form['description']
        type = int(request.form['eventype'])
        print(type)
        tags = ''.join(request.form['hashtag'].split(','))
        #SAUJAS, WE DONT HAVE DESCRIPTION
        #type = request.form['eventype']
        user_id = db.engine.execute("SELECT id FROM user WHERE username == :username", {'username': username}).fetchall()[0][0]
        insert = db.engine.execute("INSERT INTO events (name, description, venue_id, creator_id, start_time, end_time, type, hash) VALUES (:name, :description, :venue_id, :creator_id, :start_time, :end_time, :type, :tags)", {'name': name, 'description': description, 'venue_id': venue, 'creator_id': user_id, 'start_time': session['start'], 'end_time': session['end'], 'type': type, 'tags':tags})
        event_id = insert.lastrowid
        venue_details = db.engine.execute("SELECT * FROM venues WHERE id==:id", {'id': venue}).fetchall()
        db.session.commit()
        #print(db.engine.execute("SELECT * FROM events").fetchall())
        date = time.strftime("%d/%m/%Y", time.localtime(session['start']))
        start = time.strftime("%H:%M", time.localtime(session['start']))
        end = time.strftime("%H:%M", time.localtime(session['end']))
        event = {'date': date, 'start': start, 'end': end, 'tags': ' #'.join(tags.split('#')), 'type': ['Public', 'Private'][type], 'name': name, 'description': description}
        #print(event, venue_details)
        return render_template('confirm.html', event_id=event_id, event=event, venue=venue_details[0])


@app.route('/user/<username>/events', methods=['GET', 'POST'])
@login_required
def events(username=None):
    if request.method == 'POST':
        if request.form['action'] == 'decline':
            invitee_id = request.form['invitee']
            event_id = request.form['event']
            db.engine.execute("UPDATE invites SET status = 2 WHERE (invitee_id == :invitee AND event_id == :event)", {'invitee': invitee_id, 'event': event_id})
        if request.form['action'] == 'accept':
            invitee_id = request.form['invitee']
            event_id = request.form['event']
            db.engine.execute("UPDATE invites SET status = 1 WHERE (invitee_id == :invitee AND event_id == :event)", {'invitee': invitee_id, 'event': event_id})
        if request.form['action'] == 'delete':
            event_id = request.form['event']
            db.engine.execute("DELETE FROM events WHERE id == :id", {'id': event_id})
            db.session.commit()

    id = db.engine.execute("SELECT id FROM user WHERE username == :username", {'username': username}).fetchall()[0][0]
    public_events = db.engine.execute(
        "SELECT * FROM events WHERE type == 0").fetchall()
    private_events = db.engine.execute(
        "SELECT * FROM events WHERE type == 1 AND ((id IN (SELECT event_id FROM invites WHERE invitee_id == :id AND status == 1)) OR creator_id == :id)", {'id': id}).fetchall()
    invitations = db.engine.execute("SELECT * FROM events WHERE type == 1 AND (id IN (SELECT event_id FROM invites WHERE invitee_id == :id AND status == 0))", {'id': id}).fetchall()
    print(invitations)
    public_events_list = get_event_data_multiple(public_events)
    private_events_list = get_event_data_multiple(private_events)
    invitations_list = get_event_data_multiple(invitations)
    return render_template('events.html', public_events=public_events_list, private_events=private_events_list, invitations=invitations_list, invitee_id=id)


@app.route('/user/<username>/invite/<int:event_id>', methods=['GET', 'POST'])
@login_required
def invite(username=None, event_id=None):
    #print(db.engine.execute("SELECT * FROM user").fetchall())
    if request.method == 'GET':
        #invite = db.engine.execute(
        #    "SELECT * FROM invites WHERE event_id == :event_id", {'event_id': event_id})
        accepted_invites = db.engine.execute("SELECT username FROM user WHERE id IN (SELECT invitee_id FROM invites WHERE event_id == :event_id AND status == 1)", {'event_id': event_id}).fetchall()
        declined_invites = db.engine.execute("SELECT username FROM user WHERE id IN (SELECT invitee_id FROM invites WHERE event_id == :event_id AND status == 2)", {'event_id': event_id}).fetchall()
        pending_invites = db.engine.execute("SELECT username FROM user WHERE id IN (SELECT invitee_id FROM invites WHERE event_id == :event_id AND status == 0)", {'event_id': event_id}).fetchall()
        return render_template('invite.html', accepted=accepted_invites, declined=declined_invites, pending=pending_invites, event=event_id, failed=False)
    elif request.method == 'POST':
        invitee = request.form['invitee']
        failed=False
        try:
            inviter_id = db.engine.execute("SELECT id FROM user WHERE username == :username", {'username': username}).fetchall()[0][0]
            invitee_id = db.engine.execute("SELECT id FROM user WHERE username == :username", {'username': invitee}).fetchall()[0][0]
            if inviter_id == invitee_id:
                invite = db.engine.execute("SELECT username FROM user WHERE id IN (SELECT invitee_id FROM invites WHERE event_id == :event_id)", {
                                           'event_id': event_id}).fetchall()
                return render_template('invite.html', invite=invite, event=event_id)
            db.engine.execute("INSERT INTO invites (inviter_id, invitee_id, event_id, status) VALUES (:inviter_id, :invitee_id, :event_id, 0)", {'inviter_id': inviter_id, 'invitee_id': invitee_id, 'event_id': event_id})
            db.session.commit()
        except:
            failed=True
        accepted_invites = db.engine.execute("SELECT username FROM user WHERE id IN (SELECT invitee_id FROM invites WHERE event_id == :event_id AND status == 1)", {'event_id': event_id}).fetchall()
        declined_invites = db.engine.execute("SELECT username FROM user WHERE id IN (SELECT invitee_id FROM invites WHERE event_id == :event_id AND status == 2)", {'event_id': event_id}).fetchall()
        pending_invites = db.engine.execute("SELECT username FROM user WHERE id IN (SELECT invitee_id FROM invites WHERE event_id == :event_id AND status == 0)", {'event_id': event_id}).fetchall()
        return render_template('invite.html', accepted=accepted_invites, declined=declined_invites, pending=pending_invites, event=event_id, failed=failed)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.debug()
    app.run(debug=True)
