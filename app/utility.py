from app import db
import time

def get_event_data_single(event):
    venue_name = db.engine.execute("SELECT name FROM venues WHERE id == :id", {'id': event[3]}).fetchall()[0][0]
    try:
        creator = db.engine.execute("SELECT username FROM user WHERE id == :id", {'id': event[4]}).fetchall()[0][0]
    except:
        creator = ''
    date = time.strftime("%d/%m/%Y", time.localtime(event[5]))
    start = time.strftime("%H:%M", time.localtime(event[5]))
    end = time.strftime("%H:%M", time.localtime(event[6]))
    return {'id': event[0], 'name': event[1], 'description': event[2], 'date': date, 'start_time': start, 'end_time': end, 'venue': venue_name, 'creator': creator, 'tags': ' #'.join(event[7].split('#')), 'type': ['Public', 'Private'][event[8]]}

def get_event_data_multiple(query_list):
    event_list = list()
    for event in query_list:
        # venue_name = db.engine.execute("SELECT name FROM venues WHERE id == :id", {'id': event[3]}).fetchall()[0][0]
        # try:
        #     creator = db.engine.execute("SELECT username FROM user WHERE id == :id", {'id': event[4]}).fetchall()[0][0]
        # except:
        #     creator = ''
        # date = time.strftime("%d/%m/%Y", time.localtime(event[5]))
        # start = time.strftime("%H:%M", time.localtime(event[5]))
        # end = time.strftime("%H:%M", time.localtime(event[6]))
        event_list.append(get_event_data_single(event))
    return event_list
