import random 
from src.endpoints import Endpoints 
from datetime import datetime, timedelta
import logging


class Coach:
    def __init__(self, history, env="development") -> None:
        self.history = history 
        self.notif_sent = False
        self.msgs = None
        self.ep = Endpoints(env)

    def get_last_session(self, patient_id):
        last_session = None
        sessions = self.history[patient_id]["SESSIONS"]
        if sessions:   
            last_session =  Session(sessions[-1])
        return last_session

    def notifs_sent_today(self, patient_id):
        date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        messages = self.history[patient_id]['MESSAGES']
        n = 0
        for m in messages:
            if datetime.strptime(m['LAUNCH_DATETIME'], date_format).date() == datetime.today.date():
                n+=1
        return n
        
    def select_message(self, msg_list, patient_id):
        patient_history = self.history[patient_id]
        msg_dict = {i:0 for i in msg_list}
        for m in patient_history['MESSAGES']:
            if m["MESSAGE"] in msg_dict:
                msg_dict[m["MESSAGE"]] +=1
        return min(msg_dict, key=msg_dict.get)
    
    def get_streak_len(self, patient_id):
        date_format = '%Y-%m-%d %H:%M'
        patient_history = self.history[patient_id]
        streak_len = 0
        streak = True
        session_dates = [datetime.strptime(i['STARTING_DATE'], date_format).date() for i in patient_history['SESSIONS']]
        
        while streak:
            if (datetime.today().date() - timedelta(days=streak_len+1)) in session_dates:
                streak_len +=1
            else:
                streak = False
        return streak_len

    def session_reminder_scheduled(self, patient, launch_datetime):
        date_format = '%Y-%m-%d %H:%M'
        patient_history = self.history[patient.id]
        if len(patient_history["MESSAGES"])>0:
            for msg in patient_history["MESSAGES"]:
                if msg["TYPE"] != "NOTIFICATION":
                    continue
                msg_time =  datetime.strptime(msg['LAUNCH_DATETIME'], date_format)
                print(launch_datetime)
                print(msg_time)
                if abs((msg_time - launch_datetime).total_seconds()) < 300:
                    print("same")
                    return True
        return False
    
    def calculate_personality(self, patient_id):
        return (random.randint(1, 3)) 
    
    def pick_message(self, patient_id, personality, usecase):
        msg_list = self.msgs[usecase][f'v{personality}']
        return self.select_message(msg_list, patient_id)
    
    def send_mid_session_reminder(self, patient_id, personality):
        message = self.pick_message(patient_id, personality, "mid_session_reminder")
        launch_datetime = (datetime.now() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
        self.ep.schedule_notif(patient_id, message, launch_datetime, personality)

    def send_not_connected_since_days_reminder(self, patient_id, personality, days=1):
        message = self.pick_message(patient_id, personality, "not_connected_since_days_reminder")
        launch_datetime = (datetime.now() + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
        self.ep.schedule_notif(patient_id, message, launch_datetime, personality)

    def schedule_session_reminder(self, patient, personality):
        message = self.pick_message(patient.id, personality, "session_reminder")
        launch_datetime = (patient.slot.start_time - timedelta(minutes=30))
        if self.session_reminder_scheduled(patient, launch_datetime):
            logging.info("session reminder already scheduled")
            return 
        logging.info("scheduling next day reminder")
        launch_datetime = launch_datetime.strftime("%Y-%m-%d %H:%M:%S")
        self.ep.schedule_notif(patient.id, message, launch_datetime, personality)

        
    def send_streak_reminder(self, patient_id, personality, streak_len):
        message = self.pick_message(patient_id, personality, "streak_reminder")
        message = message.replace(" X", f" {str(streak_len)}")
        message = message.replace(" x", f" {str(streak_len)}")
        launch_datetime = (datetime.now() + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
        self.ep.schedule_notif(patient_id, message, launch_datetime, personality)

    def send_out_of_slot_no_streak_reminder(self, patient_id, personality):
        message = self.pick_message(patient_id, personality, "out_of_slot_no_streak_reminder")
        launch_datetime = (datetime.now() + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
        self.ep.schedule_notif(patient_id, message, launch_datetime, personality)

    def send_progress_reminder(self, patient_id, personality):
        logging.info("sending progress reminder")
        pass

class Session:
    def __init__(self, session):
        date_format = '%Y-%m-%d %H:%M'
        self.start_time = datetime.strptime(session["STARTING_DATE"], date_format)
        self.score = session['SCORE']
        self.duration = session['SESSION_DURATION_SECONDS']
