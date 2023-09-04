#!/usr/bin/env python
# coding: utf-8

# In[5]:


from rasa.nlu.model import Interpreter


# In[6]:


import random
import spacy
from spacy.matcher import Matcher
import requests


# In[7]:


import paho.mqtt.client as mqtt
import json


# In[8]:


interpreter = Interpreter.load('C:\\Users\\Aditya Roy\\Desktop\\Jarvis 2.0\\nlu_20191009-142926')


# In[9]:


nlp = spacy.load('en_core_web_lg')


# In[10]:


def respond(user_text):
    doc = nlp(user_text)
    matcher = Matcher(nlp.vocab)
    matcher = setupMatcher(matcher)
    predictions = interpreter.parse(user_text)
    intent = predictions['intent']['name']
    if intent == 'greet':
        return greet(user_text,doc,matcher)
    elif intent == 'bye':
        return bye()
    elif intent == 'room_control':
        return room_control(predictions)
    elif intent == 'weather':
        return weather()
    elif intent == 'RoomTemperature':
        return room_temp()
    elif intent == 'MutePhone':
        return mute_android()
    elif intent == 'CreateContact':
        return 'I am still learning to do that'
    elif intent == 'PCControls':        
        return turn_off_pc()


# In[11]:


def greet(text,spacyData,matcher):

    responses = ['Fine','I am doing great, what about you?','Hey','Hii','Hey there!']
    last_char = text[len(text) -1]
    matches = matcher(spacyData)
    if len(matches)>0:
        for match_id, start, end in matches:
            matched_span = doc[start:end].text
            return firstCaps(matched_span)
    if last_char == '?':
        if(findSpeechTag(spacyData,'VERB')):
            return 'Hi, I am fine'
    else:
        return random.choices(responses)[0]
    


# In[12]:


def bye():
    responses = ['Bye','See you later','Goodbye']
    return random.choice(responses)[0]


# In[13]:


def send_appliance_request(trigger_event):
    URL = 'https://maker.ifttt.com/trigger/{}/with/key/btWpzwu3bOWNpC98zAPRRU'.format(trigger_event)
    response = requests.get(url = URL)
    print(response.json)


# In[14]:


def weather():
    return get_weather_response('Jamshedpur','India')
    


# In[15]:


def room_temp():
    return 'I am currently working on it'
    


# In[16]:


def turn_off_pc():
    jrv_response = ['Ok, shutting down your pc','Ok taking a shutdown of your PC','Ok switching off your pc']
    response = get_response_json('https://maker.ifttt.com/trigger/pc_shutdown/with/key/bflBylSmb9qf8DBCf2E0K-')
    return random.choices(jrv_response)[0]


# In[17]:


def get_weather_response(city,country):
    key = 'eedcd05f19e509cd79334c5dd1a4d05e'
    URL = "http://api.openweathermap.org/data/2.5/weather?q={},{}&appid={}&units={}".format(city,country,key,'metric')
    response = get_response_json(URL)   
    des,temp,pres = response['weather'][0]['main'],response['main']['temp'],response['main']['pressure']
    reply= {'Country':country,'City':city,'Temp':temp,'Des':des,'Pressure':pres}
    return reply


# In[18]:


def get_respoonse_json(URL):
    return requests.get(url = URL).json()


# In[19]:


def firstCaps(text):
    text = text+ ' '
    p =  0
    newSen = ' '
    i = 0
    for c in text:
        
        if c == ' ':
            word = text[p:i]
            p = i + 1
            i = i + 1
            word = word.capitalize()
            newSen = newSen + word + ' '

        i = i +1
    return newSen


# In[20]:


def mute_android():
    jrv_response = ['Ok muting your phone','Ok I am muting your mobile','Ok Aditya, I am muting your mobile']
    reponse= get_response_json('https://maker.ifttt.com/trigger/android_mute/with/key/bflBylSmb9qf8DBCf2E0K-')
    return random.choices(jrv_response)[0]


# In[21]:


def findSpeechTag(doc,tag):
    for token in doc:
        if token.pos_ == tag:
            return True
    return False    
    


# In[22]:


def setupMatcher(matcher):
    patterns = [[{'LEMMA':'good'},{'POS':'NOUN'}]]
    i = 0
    for pattern in patterns:
        matcher.add('Pattern'+str(i),None,pattern)
        return matcher


# In[23]:


def on_connect(client,userdata,flags,rc):
    print('Connected with result_code'+rc)
    client.subscribe('/Jarvis')
    


# In[30]:


def on_message(client,userdata,msg):
    msgObject = json.loads(msg.payload())
    print(msgObject)
    auth_token = msgObject["AUTH_TOKEN"]
    publish_topic = msgObject["DEVICE_ID"]
    user_text = msgObject["USER_TEXT"]
    
    
    client("/{}".format(publish_topic),"Test")


# In[27]:


def authenticateRequest(token):
    if token == 'AbhiNaJaoChorKar':
        return 0
    else:
        return -1


# In[ ]:


client = mqtt.Client()
client.on_message = on_message
client.on_connect = on_connect
print('Connecting')
client.connect('192.168.43.136',1883)
print('Connected')
client.loop_forever()


# In[ ]:




