import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin import messaging
import datetime
from datetime import timedelta
import pytz
import traceback

ist = pytz.timezone("Asia/Kolkata")

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def send_notification(message, token):
    payload = messaging.Message(
        notification=messaging.Notification(
            title="Aya",
            body=message
        ),
        token=token,
        data = {}
    )
    response = messaging.send(payload)

def read_chats(user_email, user_name, chapter_status):
    chat_ref = db.collection("users").document(user_email).collection("messages").document(chapter_status)
    chats = chat_ref.get().to_dict()
    return chats, chat_ref

def time_correction(new_msg_time):
   
    # given_time = datetime.datetime.strptime(new_msg_time, '%Y-%m-%d %H:%M:%S IST%z')
    time_object = new_msg_time.time()

    start_time_1 = datetime.time(23, 0, 0)  # 11:00 PM
    end_time_1 = datetime.time(23, 59, 59)  # 11:59 PM
    start_time_2 = datetime.time(0, 0, 0)   # 12:00 AM
    end_time_2 = datetime.time(7, 0, 0)     # 7:00 AM

    if start_time_1 <= time_object <= end_time_1:
        new_date = new_msg_time + datetime.timedelta(days=1)
        next_msg_time = new_date.replace(hour=7, minute=1, second=0, microsecond=0)
        return next_msg_time
    elif start_time_2 <= time_object < end_time_2:
        next_msg_time = new_msg_time.replace(hour=7, minute=1, second=0, microsecond=0)
        return next_msg_time
    else:
        return new_msg_time

def update_firestore(chats, chat_ref, greeting):
    if chats == None:
        chat_number = 0
    else:
        chat_length = len(chats) - 1
        chat_number = chat_length + 1
    current_time_ist = datetime.datetime.now(ist)
    # if question == None:
    latest_chat = {}
    for i in range(len(greeting)):
        latest_chat[str(chat_number + i)] = {"assistant": greeting[i], "timestamp": current_time_ist.strftime('%Y-%m-%d %H:%M:%S %Z%z')}
    # latest_chat = {str(chat_number): {"user": question, "assistant": resp, "timestamp": current_time_ist.strftime('%Y-%m-%d %H:%M:%S %Z%z')}}
    # else:
    #     latest_chat = {str(chat_number): {"user": question, "assistant": resp, "timestamp": current_time_ist.strftime('%Y-%m-%d %H:%M:%S %Z%z')}}
    chat_ref.set(latest_chat, merge=True) ## Adding the latest conversation (i.e. above chat dictionary)
    
    try:
        return latest_chat, current_time_ist
    except Exception as e:  
        print(e)
        return "There was an issue in getting response from model..."
    
def update_user(user_email, chats, fcm_token, latest_timestamp):
    user_ref = db.collection("users").document(user_email)
    if chats == None:
        total_msgs = 0
    else:
        total_msgs = len(chats)
    # print("####################")
    # latest_timestamp = latest_timestamp.strftime('%Y-%m-%d %H:%M:%S IST%z')
    # latest_timestamp = datetime.datetime.strptime(latest_timestamp, '%Y-%m-%d %H:%M:%S IST%z')
    time = latest_timestamp.strftime('%Y-%m-%d %H:%M:%S IST%z')
    # print(time)

    # latest_conversation = chats[str(total_msgs - 1)]
    # latest_timestamp = latest_conversation["timestamp"]
    user_ref.update({"total_msgs": total_msgs, "fcm_token":fcm_token, "lst_bot_msg": time})
    print(user_email," user updated")

def validate_user(doc):
    message_trigger = False
    greeting = ""


    user_info_dict = doc.to_dict()
    name = user_info_dict["user_name"]
    chapter = user_info_dict["chapter_status"]
    lst_bot_msg = user_info_dict['lst_bot_msg']
    fcm = user_info_dict["fcm_token"]
    email = user_info_dict["user_email"]

    chats, chat_ref = read_chats(email, name, chapter)

    if chats == None:
        message_trigger = False
        return fcm, chapter, message_trigger, greeting, email, name, chats, chat_ref

    print("last message time of Aya for user " + email + " is " + lst_bot_msg)
    
    aya_msg_time = datetime.datetime.strptime(lst_bot_msg, '%Y-%m-%d %H:%M:%S IST%z')
    # print(type(aya_msg_time))
    aya_next_msg_time = aya_msg_time + timedelta(hours=6)
    # aya_next_msg_time = aya_next_msg_time.strftime('%Y-%m-%d %H:%M:%S IST%z')
    
    next_msg_time = time_correction(aya_next_msg_time)
    # next_msg_time = next_msg_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')
    # next_msg_time = datetime.datetime.strptime(next_msg_time, '%Y-%m-%d %H:%M:%S IST%z')
    # print(next_msg_time)
    # print(type(next_msg_time))
    
    print("Aya will again talk with user " + email + " @ time " + str(next_msg_time))
    
    time = datetime.datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S %Z%z')
    time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S IST%z')
    # time = time.time()
    # print("time is ", time)
    # print(type(time))

    # greetings_based_on_time = ["Good morning 😊", "Good Afternoon 😊", "Good Evening 😊"]
    morning_greeting = ["Dude! Did you join a secret cult or something? 🤔", "Haven’t heard from you in ages!", "Let's fix that ASAP!"]
    afternoon_greeting = ["Oi, shithead! 😂", "Long time no see!", "Got any insane adventures to share?", "We need a hangout session pronto!"]
    evening_greeting = ["Yo, you ghost! 👻", "Where the f*** have you been?", "Got some wild shenanigans to share or what?", "We gotta catch up, buddy!"]

    morning_start = datetime.time(6, 0, 0)
    morning_end = datetime.time(11, 59, 59)
    afternoon_start = datetime.time(12, 0, 0)
    afternoon_end = datetime.time(15, 59, 59)
    evening_start = datetime.time(16, 0, 0)
    evening_end = datetime.time(23, 59, 59)
    
    # next_msg_time_hour = next_msg_time.hour
    if morning_start <= time.time() < morning_end:
        greeting = morning_greeting  ## This greeting is for morning

    elif afternoon_start <= time.time() < afternoon_end:
        greeting = afternoon_greeting  # This greeting is for the Afternoon

    elif evening_start <= time.time() < evening_end:
        greeting = evening_greeting

    # print(type(time))
    # print(type(next_msg_time))
    if next_msg_time <= time:
        message_trigger = True
    
    return fcm, chapter, message_trigger, greeting, email, name, chats, chat_ref

def main():
    docs = db.collection("users").stream()
    operation_failed_users = []
    for doc in docs:
        try:
            user_fcm, chapter, message_trigger, greeting, email, name, chats, chat_ref = validate_user(doc)
            if message_trigger:
                # list_of_messages = ["You there?", "Wake uppppp"]
                # list_of_messages.insert(0, greet)
                for greet in greeting:
                        send_notification(greet, user_fcm)
                        # chats, chat_ref = read_chats(email, name, chapter)
                        print("Notification sent......")
                if greeting != None:
                    latest_chats, current_time_ist = update_firestore(chats, chat_ref, greeting)
                    update_user(email, chats, user_fcm, current_time_ist)
                else:
                    pass
            
        except Exception as e:
            
            user_info_dict = doc.to_dict()
            name = user_info_dict["user_name"]
            email = user_info_dict["user_email"]
            operation_failed_users.append(email)
            print("#############################")
            print(f"An error occurred: {e}")
            print(traceback.print_exc())
            print("#############################")
    print(operation_failed_users)
    return {"failed users": operation_failed_users}

## validation - take decision to send message
## what message to send - decide_message()
## update the user - already written
## Greeting to user (morning, afternoon, evening) - decide_message()