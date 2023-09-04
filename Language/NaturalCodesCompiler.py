#!/usr/bin/env python
# coding: utf-8

# In[ ]:


print('Welcome to Natural Codes')
print('Please wait while we get ready')
print('Loading Interpreter....')
from rasa_nlu.model import Interpreter
import re
import subprocess

# In[3]:


interpreter = Interpreter.load('C:\\Users\\Aditya Roy\\Desktop\\Compiler3\\default\\model_20190919-134818')


# In[4]:


print('Interpreter Loaded.')
print('Loading modules....')
import spacy
nlp = spacy.load('en_core_web_lg')


# In[39]:



print('Modules Loaded.')


# In[ ]:


counter = 0
giveSpace = False
removeSpace = False
hasToBeConverted = False
con_var = None
con_type = None
setConversion = False

whole_vars = []
real_vars =  []
str_vars = []
def parse_to_python(code):
    global counter
    global giveSpace
    global removeSpace
    global last_in
    global con_var
    global con_type
    global hasToBeConverted
    global setConversion
    text = []
    
    if code[len(code) - 1] == '.':
        code = code[:len(code)-1]
        removeSpace = True
        last_in = 1
    else:
        last_in = 0

    processed_code = None
    while True:
        code,quoted_text = messageExtractorAndCodeFormatter(code)   
        if quoted_text == None:
            break
        else:
            text.append(quoted_text)    
    data = interpreter.parse(code)
    doc = nlp(code)
    intent = data['intent']['name']
    entities = data['entities']   
    
    if intent == 'input':
        if len(text) is 0:
            inMessage = ""
        else:
            inMessage = "'{}' +'\\n'".format(text[0])

        var = doc[doc.__len__()-1]
        if len(entities)== 0:
            processed_code = var.text+" = str(input({})".format(inMessage)
        elif entities[0]['value']=='whole number':
            processed_code = var.text+" = int(input({}))".format(inMessage)
        elif entities[0]['value']=='real number':
            processed_code = var.text+" = float(input({}))".format(inMessage)
        
    elif intent == 'print':
        
        if len(entities) != 0:
            startIndex = entities[0]['end']
            message = nextWordExtractor(code[startIndex:])
        elif text is None:
            message = doc[doc.__len__()-1]
        else:    
            message = text[0]

        processed_code = "print('{}')".format(message)
   
    elif intent == 'declaration':
        var = nextWordExtractor(code[entities[0]['end']:])
        con_var = var
        con_type = entities[1]['value']
        setConversion = True
        processed_code = "{} = None".format(var)
      
    
    elif intent == 'loop':
        
        p1 = code[entities[0]['end']+1:entities[1]['start']-1].strip()
        p2 = code[entities[1]['end']+1:len(code)]
        op = operator_finder(entities[1]['value'])
        processed_code = 'while {} {} {}:'.format(p1,op,p2)
        giveSpace = True    
                
    
    elif intent == 'condition':
        cond = entities[0]['value']
        if cond == 'else':
            processed_code= 'else:'
        else:
            if cond.lower() == 'else if':
                cond = 'elif'
            index = []
            for idx,entity in enumerate(entities):
                if idx == 0:
                    continue
                op =entity['value']
                for token in doc:
                    if token.text == op:
                        if token.i in index:
                            continue
                        else:    
                            index.append(token.i)
            for idx,indx in enumerate(index):                        
                p1 = doc[indx - 1]
                p2 = doc[indx + 1]
                if idx == 0:
                    processed_code = '{} {} {} {}'.format(cond,p1,operator_finder(op),p2)
                else:
                    processed_code+= ' and {} {} {}'.format(p1,operator_finder(op),p2)   
            processed_code+=':'   
        giveSpace = True      
        
    
    
    elif intent == 'assign':
        ent1_out = entities[0]['end']
        ent2_in = entities[1]['start']
        ent2_out = entities[1]['end']
        var1 = code[ent1_out+1:ent2_in].strip()
        var2 = code[ent2_out+1:len(code)]
        hasToBeConverted = True
    
        con_var = var2
        processed_code = "{} = {}".format(var2,var1)
        
    elif intent =="'Calculate'":
        eq = None
        for document in doc:
            if document.text == "and" or doc.text == 'And' or doc.text == ',':
                refined_text = doc[0:document.i]                
                equ_start = entities[1]['end']
                equ_stop = len(refined_text.text)
                eq =  refined_text.text[equ_start:equ_stop]
               
        var = doc[len(doc) - 1]
        hasToBeConverted = True
        con_var = var.text

        processed_code = "{} = {}".format(var, eq)
        
    elif intent == "Collection":
        if len(entities)>0:
            var = nextWordExtractor(code[entities[0]['end']:])
        else:
            var = doc[doc.__len__()-1]
        processed_code = "{} = []".format(var)
    
    elif intent == "'ForEach'":
        var1 = text[0]
        var2 = text[1]
        processed_code = "for {} in {}:".format(var1,var2)
        giveSpace = True
    
    elif intent == "ArrayGet":
        if len(text)<3:
            return
        
        index = getNumberFromString(text[0])
        arrayName = text[1]
        storeVariable = text[2]
        if index -1 <0:
            index = text[0]
            
        processed_code = "{} = {}[{}]".format(storeVariable,arrayName,index)    
        
        
    elif intent == "ArrayInsert":
        hasIndex = False
        
        for enty in entities:
            if enty['entity'] == 'at':
                hasIndex = True
            elif enty['entity'] == 'in':
                var = nextWordExtractor(code[enty['end']:])
            elif enty['entity'] == 'value':
                value = nextWordExtractor(code[enty['end']:])
                
        if not checkIfNumber(value):
               value = "'{}'".format(value)
            
        if hasIndex:
            ndx = getNumberFromString(text[0])

            if ndx - 1<0:
                pos = text[0]
                processed_code = '{}[{}] = {}'.format(var,pos,value)
            else:
                pos = ndx
                processed_code = '{}[{}] = {}'.format(var,pos-1,value)
           
        else:
            processed_code = '{}.append({})'.format(var,value)
    
    if setConversion:
        putInConversionList(con_var,con_type)
        setConversion = False
    
    con_code = ""
    result = printer_(processed_code,counter)
    if hasToBeConverted:
        con_code = getConversionLineOfCode(con_var)
        con_code = printer_(con_code,counter)
        hasToBeConverted = False
   
    
    if giveSpace:
        counter = counter+ 1
        giveSpace = False
    if removeSpace:
        counter = counter-1
        removeSpace = False
    return result, con_code 


# In[ ]:


import sys 
def start_app():
    lang_code_path = 'C:\\Users\\Aditya Roy\\Desktop\\Language\\code.txt'
    python_file_path = 'C:\\Users\\Aditya Roy\\Desktop\\Language\\Prog_Python.py'
    code_file = open(lang_code_path,'r')
    python_file = open(python_file_path,'w+')
    lines = code_file.readlines()
    python_file.write('def  __main__():\r\n')
    for line in lines:
        line = line.strip()
        if line == "" or line == "\n":
            continue
        if line[len(line)-1] == '\n':
            line  = line[0:len(line)-1]
        
        py_code,con_code = parse_to_python(line)
        if py_code is None:
            continue
            
        python_file.write('\t'+py_code+'\r')
        if con_code is not None:    
            python_file.write('\t'+con_code+'\r')
    python_file.write('__main__()\r')
    python_file.close()


# In[ ]:


def menu():
    print("1)Run the program")
    print("2)Exit")
    choice = int(input('Enter option number'+'\n'))
    if choice == 1:
        start_app()
        subprocess.call([r'open.bat'])
        menu()
    elif choice == 2:
        print('Exiting app...')
        return
    else:
        print('Please enter correct option number')
        menu()


# In[ ]:


def nextWordExtractor(text):
    text = text.strip() + ' '
    for i in range(0,len(text)):
        if text[i] == ' ':
            return text[:i]


# In[ ]:


def messageExtractorAndCodeFormatter(code):
    start, end = getQuotedTextIndexes(code)
    if start == -1 or end == -1:
        return code,None
    text = code[start + 1:end]
    code = code[0:start].strip()+" "+code[end+1:len(code)].strip()
    return code,text


# In[ ]:


def checkIfNumber(value):
    isNumber = False
    c = value.strip()[0]
    if ord(c)>= ord('0') and ord(c)<=ord('9'):
        isNumber = True
    return isNumber


# In[ ]:


def getNumberFromString(s):
    number = 0
    for c in s:
        if ord(c)>= ord('0') and ord(c)<=ord('9'):
            number =  number * 10
            number = number +  (ord(c) - ord('0'))
    return number


# In[ ]:


def getQuotedTextIndexes(text):
    i = 0
    start = -1
    end = -1
    quoteCounter = 0
    for c in text:
        if c == "'":
            if (quoteCounter == 2):
                break
            elif quoteCounter == 0:
                quoteCounter = quoteCounter + 1
                start = i
            elif quoteCounter == 1:
                quoteCounter = quoteCounter + 1
                end = i
        i = i + 1
    if start>=0 and end>=0:
        return start,end
    else:
        return -1,-1


# In[ ]:


def getConversionLineOfCode(var):
    if var in whole_vars:
        return "{} = int({})".format(var,var)
    elif var in real_vars:
        return "{} = float({})".format(var,var)
    elif var in str_vars:
        return "{} = str({})".format(var,var)
    else:
        return None


# In[ ]:


def putInConversionList(var,var_type):
    if var_type == "whole number":
        whole_vars.append(var)
    elif var_type == "real number":
        real_vars.append(var)
    elif var_type == "string":
        str_vars.append(var)


# In[ ]:


def operator_finder(word):
    if word == 'less_than_equal':
        return '<='
    elif word == 'more_than_equal':
        return '>='
    elif word == 'less_than':
        return '<'
    elif word == 'more_than':
        return '>'
    elif word == 'equals':
        return '=='


# In[ ]:


def printer_(code,counter):
    pr_code = ""
    for i in range(0,counter):
        pr_code+="   "
    
        
    pr_code= pr_code+code
    
    return pr_code


# In[ ]:


menu()


# In[ ]:





# In[ ]:




