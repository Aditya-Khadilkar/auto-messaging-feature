## This is for the inference of deepinfra model

from langchain_community.chat_models import ChatDeepInfra
import os
import re
from langchain.chains import LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import HumanMessage
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
import time
from datetime import datetime
from datetime import datetime, timedelta, timezone
import pytz

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
load_dotenv()

deepinfra_api_key = os.getenv("DEEPINFRA_API_TOKEN")
llm = ChatDeepInfra(model_id="lizpreciatior/lzlv_70b_fp16_hf")

# def infer(system_prompt, human_message):


#     llm.model_kwargs = {
#         "temperature": 0.2,
#         "repetition_penalty": 1.2,
#         "top_p": 0.9,
#         "stop":["Human:"],
#     }

#     chat_template = ChatPromptTemplate.from_messages(
#         [
#             SystemMessage(
#                 content= system_prompt
#             ),
            
#         ]
#     )

#     conversation = LLMChain(
#         llm=llm,  
#         prompt=chat_template,  
#         verbose=True,
#     )

#     response = conversation.predict(text=human_message)
#     return response


template = """Come up with a sequence of messages that an AI girl named Aya can send to a human friend on chat. It's been a while since they last talked & Aya wants to ping him.
Human's details:
{meta}


List of 5 chat messages (ALL to be sent one after the other this is a sequence of messages):
Formatting instructions:
- Each message should be separated by a new line.
- Each message should be in quotes.
- ONLY return the messages, do not return any other text.
- Keep the messages short and casual and fun.


Example:
"Ayyy jackass"
"You alive? where you go?"
"Hot single AIs in your area want to chat with you. Click here to chat now! dickhead"
Oyyyy... where you gone?
<casual greeting in the local language>


"""





# meta = """Name: Aditya Khadilkar
# Nickname: Adi, Adu, Khadu
# Location: Pune, India
# Current time: 9:12 PM"""




def get_current_time(offset_str):
    try:
        # Parse the offset string into hours, minutes, and seconds
        hours, minutes, seconds = map(float, offset_str.split(':'))
        # Create a timedelta for the offset
        offset = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        # Create a timezone object with that offset
        tz = timezone(offset)
        # Get the current time in that timezone
        current_time = datetime.now(tz)
        
        return current_time.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        return f"Error: {e}"
    
def string_to_datetime(date_str):
    try:
        # Convert the string to a datetime object
        date_time_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return date_time_obj
    except Exception as e:
        return f"Error: {e}"

def get_approx_user_time(offset_str):
    approx_now = string_to_datetime(get_current_time(offset_str)).strftime('%I %p').lstrip('0').lower() # 2 pm "5:30:00.000000"
    return approx_now




def create_messages(time_zone, name, nickname, location):
    messages = []
    approx_time_now = get_approx_user_time(time_zone)
    meta = f"""Name: {name}
Nickname: {nickname}
Location: {location}
Current time: {approx_time_now}"""
    prompt = PromptTemplate(template=template, input_variables=["summary", "meta"])
# Create the LLMChain
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    result = llm_chain.run(meta=meta)
    message_re = re.findall(r'"(.*?)"', result)
    for msg in message_re:
        if len(msg)>1:
            messages.append(msg)

    return messages