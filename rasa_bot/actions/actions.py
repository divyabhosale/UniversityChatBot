# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
import requests
import json
import spacy
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionGetDesc(Action):

    def name(self) -> Text:
        return "action_course_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = tracker.latest_message.get('text')
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(message)
        course_name = ''
        course_number = ''
        for token in doc:
            #print(token.text,token.tag_)
            if token.tag_ == 'NNP' or token.tag_ == 'NN':
                course_name = token.text
            if token.tag_ == 'CD':
                course_number = token.text

        if course_number == '':
            course_number = course_name[4:len(course_name)]
            course_name = course_name[0:4]
	
        url = 'http://localhost:3030/project/query'
        
        spql_query = f"""PREFIX dc: <http://purl.org/dc/elements/1.1/>
				PREFIX np: <http://www.nanopub.org/nschema#>
				PREFIX npg: <http://ns.nature.com/terms/>
				PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
				PREFIX focu: <http://focu.io/schema#>
				PREFIX focup: <http://focu.io/schema/property#>
				SELECT ?course ?description
                WHERE{{
                ?course rdf:type focu:Course .
                ?course dc:description ?description .
                ?course npg:number {course_number} .
                ?course focup:belongs_to "{course_name}".
                }}"""
                
        myobj = {'query': spql_query}
        x = requests.post(url, data = myobj)    
        desc = json.loads(x.text)['results']['bindings'][0]['description']['value']

        #print(x.text)
        dispatcher.utter_message(text=desc)
        #dispatcher.utter_message(text=message)


        return []


class ActionGetTopics(Action):

    def name(self) -> Text:
        return "action_topic_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = tracker.latest_message.get('text')
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(message)
        topic = ''
        for token in doc:
            #print(token.text,token.tag_)
            if token.tag_ != 'WDT' and token.tag_ != 'NNS' and token.tag_ != 'VBP' and token.tag_ != '.':
                topic += token.text +' '
           
        topic = topic.strip().lower()   
	
        url = 'http://localhost:3030/project/query'
        
        spql_query = f"""PREFIX dc: <http://purl.org/dc/elements/1.1/>
				PREFIX np: <http://www.nanopub.org/nschema#>
				PREFIX npg: <http://ns.nature.com/terms/>
				PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
				PREFIX focu: <http://focu.io/schema#>
				PREFIX focup: <http://focu.io/schema/property#>
				PREFIX foaf: <http://xmlns.com/foaf/0.1/>
				PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
				PREFIX schema: <http://schema.org/>
				SELECT ?course_name ?course_subject ?course_number
				WHERE
				{{
				?topic rdf:type focu:Topic .
				?topic foaf:name ?o.
				FILTER (lcase(str(?o)) = "{topic}").
				?topic schema:isPartOf ?course .
				?course rdf:type focu:Course .
				?course foaf:name ?course_name .
				?course npg:number ?course_number .
				?course focup:belongs_to ?course_subject .
				}}"""
                
        myobj = {'query': spql_query}
        x = requests.post(url, data = myobj)    
        courselist = json.loads(x.text)['results']['bindings']
        courses = ''
        for course_detail in courselist:
            courses += course_detail['course_name']['value'] +' '
            courses += course_detail['course_subject']['value'] +' '
            courses += course_detail['course_number']['value'] +'\n'
        #print(courses)
        #print(x.text)
        dispatcher.utter_message(text=courses)


        return []


class ActionGetTopicsByEvent(Action):

    def name(self) -> Text:
        return "action_topic_info_event"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = tracker.latest_message.get('text')
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(message)
        event_details = []
        for token in doc:
            #print(token.text,token.tag_)
            if token.tag_ != 'WDT' and token.tag_ != 'NNS' and token.tag_ != 'VBP' and token.tag_ != 'VBN' and token.tag_ != 'IN' and token.tag_ != '.':
                event_details.append(token.text)
           
        url = 'http://localhost:3030/project/query'

        if event_details[0] == 'Lecture':        
            spql_query = f"""PREFIX dc: <http://purl.org/dc/elements/1.1/>
                            PREFIX np: <http://www.nanopub.org/nschema#>
                            PREFIX npg: <http://ns.nature.com/terms/>
                            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX focu: <http://focu.io/schema#>
                            PREFIX focup: <http://focu.io/schema/property#>
                            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                            PREFIX schema: <http://schema.org/>
                            PREFIX owl: <http://www.w3.org/2002/07/owl#>
                            SELECT ?topic_name ?topic_URI
                            WHERE
                            {{
                            ?topic rdf:type focu:Topic .
                            ?topic foaf:name ?topic_name.
                            ?topic owl:sameAs ?topic_URI. 
                            ?topic schema:isPartOf ?course_event .
                            ?course_event npg:number {event_details[2]} .
                            ?course_event rdf:type focu:Lecture .
                            ?course_event focup:belongs_to ?course.
                            ?course focup:belongs_to "{event_details[3]}" .
                            ?course npg:number {event_details[4]} .  
                            }}"""
        else:
            spql_query = f"""PREFIX dc: <http://purl.org/dc/elements/1.1/>
                            PREFIX np: <http://www.nanopub.org/nschema#>
                            PREFIX npg: <http://ns.nature.com/terms/>
                            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX focu: <http://focu.io/schema#>
                            PREFIX focup: <http://focu.io/schema/property#>
                            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                            PREFIX schema: <http://schema.org/>
                            PREFIX owl: <http://www.w3.org/2002/07/owl#>
                            SELECT ?topic_name ?topic_URI
                            WHERE
                            {{
                            ?topic rdf:type focu:Topic .
                            ?topic foaf:name ?topic_name.
                            ?topic owl:sameAs ?topic_URI. 
                            ?topic schema:isPartOf ?course_event .
                            ?course_event npg:number {event_details[2]} .
                            ?course_event rdf:type focu:Lab .
                            ?course_event rdfs:subClassOf ?lecture .
                            ?lecture focup:belongs_to ?course .
                            ?course focup:belongs_to "{event_details[3]}" .
                            ?course npg:number {event_details[4]} .  
                            }}"""

        myobj = {'query': spql_query}
        x = requests.post(url, data = myobj)    
        #print(x.text)
        topiclist = json.loads(x.text)['results']['bindings']
        topics = ''
        for topic_detail in topiclist:
            topics += topic_detail['topic_name']['value'] +' '
            topics += topic_detail['topic_URI']['value'] +'\n'

        dispatcher.utter_message(text=topics)


        return []


class ActionGetLab(Action):

    def name(self) -> Text:
        return "action_lab_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = tracker.latest_message.get('text')
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(message)
        event_details = []
        for token in doc:
            #print(token.text,token.tag_)
            if token.tag_ == 'NN' or  token.tag_ == 'CD':
                event_details.append(token.text)
                
        url = 'http://localhost:3030/project/query'
        spql_query = f"""PREFIX dc: <http://purl.org/dc/elements/1.1/>
                        PREFIX np: <http://www.nanopub.org/nschema#>
                        PREFIX npg: <http://ns.nature.com/terms/>
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX focu: <http://focu.io/schema#>
                        PREFIX focup: <http://focu.io/schema/property#>
                        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        SELECT ?lab ?lab_name ?lab_slides
                        WHERE
                        {{
                        ?lecture rdf:type focu:Lecture.
                        ?lecture npg:number {event_details[1]} .
                        ?lecture focup:belongs_to ?course.
                        ?course npg:number {event_details[3]} .
                        ?course focup:belongs_to "{event_details[2]}".
                        ?lab rdf:type focu:Lab.
                        ?lab focup:includes_slides ?lab_slides.
                        ?lab rdfs:subClassOf ?lecture.
                        ?lab foaf:name ?lab_name.
                        }}"""
                        
        myobj = {'query': spql_query}
        x = requests.post(url, data = myobj)    
        lablist = json.loads(x.text)['results']['bindings']
        lab_details = lablist[0]['lab_name']['value'] +' ' + lablist[0]['lab_slides']['value']
        dispatcher.utter_message(text=lab_details)


        return []

class ActionGetLectures(Action):

    def name(self) -> Text:
        return "action_lecture_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = tracker.latest_message.get('text')
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(message)
        topic = ''
        for token in doc:
            #print(token.text,token.tag_)
            if (token.tag_ == 'NN' or token.tag_ == 'NNP' or  token.tag_ == 'CD') and ( token.text != 'lecture' and token.text != 'topic'):
                topic += token.text+' '

        topic = topic.strip()       
        #print(topic)
        url = 'http://localhost:3030/project/query'

        spql_query = f"""PREFIX dc: <http://purl.org/dc/elements/1.1/>
                        PREFIX np: <http://www.nanopub.org/nschema#>
                        PREFIX npg: <http://ns.nature.com/terms/>
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX focu: <http://focu.io/schema#>
                        PREFIX focup: <http://focu.io/schema/property#>
                        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        PREFIX schema: <http://schema.org/>
                        SELECT ?topic ?lecture ?lecture_name ?lecture_slides
                        WHERE
                        {{
                        ?topic rdf:type focu:Topic .
                        ?topic foaf:name ?o.
                        FILTER (lcase(str(?o)) = "{topic}").
                        ?topic schema:isPartOf ?lecture .
                        ?lecture rdf:type focu:Lecture .
                        ?lecture foaf:name ?lecture_name .
                        ?lecture focup:includes_slides ?lecture_slides .
                        }}"""
                        
        myobj = {'query': spql_query}
        x = requests.post(url, data = myobj)    
        courselist = json.loads(x.text)['results']['bindings']
        courses = ''
        for course_detail in courselist:
            courses += course_detail['lecture_name']['value'] +' '
            courses += course_detail['lecture_slides']['value'] +'\n'

        #print(courses)
        dispatcher.utter_message(text=courses)


        return []



class ActionGetLecturesLabs(Action):

    def name(self) -> Text:
        return "action_lecture_lab_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = tracker.latest_message.get('text')
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(message)
        topic = ''
        for token in doc:
        #print(token.text,token.tag_)
            if (token.tag_ == 'NNP' or  token.tag_ == 'NNPS') and ( token.text != 'lecture' and token.text != 'topic'):
                topic += token.text+' '

        topic = topic.strip().lower()       
        #print(topic)
        url = 'http://localhost:3030/project/query'

        spql_query = f"""PREFIX dc: <http://purl.org/dc/elements/1.1/>
                        PREFIX np: <http://www.nanopub.org/nschema#>
                        PREFIX npg: <http://ns.nature.com/terms/>
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX focu: <http://focu.io/schema#>
                        PREFIX focup: <http://focu.io/schema/property#>
                        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        PREFIX schema: <http://schema.org/>
                        SELECT ?course_name ?lecture_name ?lab_name ?slides ?worksheets ?lab_slides
                        WHERE
                        {{
                        ?course rdf:type focu:Course .
                        ?course foaf:name ?course_name .
                        ?course foaf:name ?o.
                        FILTER (lcase(str(?o)) = "{topic}").
                        ?lecture focup:belongs_to ?course .
                        ?lab rdfs:subClassOf ?lecture .
                        ?lecture foaf:name ?lecture_name .
                        ?lab foaf:name ?lab_name .
                        ?lecture focup:includes_slides ?slides .
                        ?lecture focup:includes_worksheet ?worksheets .
                        ?lab focup:includes_slides ?lab_slides.
                        }}"""
                        
        myobj = {'query': spql_query}
        x = requests.post(url, data = myobj)    
        courselist = json.loads(x.text)['results']['bindings']
        courses = ''
        for course_detail in courselist:
            courses += course_detail['lecture_name']['value'] +' '
            courses += course_detail['lab_name']['value'] +' '
            courses += course_detail['slides']['value'] +' '
            courses += course_detail['worksheets']['value'] +' '
            courses += course_detail['lab_slides']['value'] +'\n\n'

        dispatcher.utter_message(text=courses)


        return []

class ActionGetSyllabus(Action):

    def name(self) -> Text:
        return "action_syllabus_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = tracker.latest_message.get('text')
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(message)
        course_name = ''
        course_number = ''
        for token in doc:
            #print(token.text,token.tag_)
            if token.tag_ == 'NNP' or token.tag_ == 'NN':
                course_name = token.text
            if token.tag_ == 'CD':
                course_number = token.text

        if course_number == '':
            course_number = course_name[4:len(course_name)]
            course_name = course_name[0:4]
            

        url = 'http://localhost:3030/project/query'

        spql_query = f"""PREFIX dc: <http://purl.org/dc/elements/1.1/>
                        PREFIX np: <http://www.nanopub.org/nschema#>
                        PREFIX npg: <http://ns.nature.com/terms/>
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX focu: <http://focu.io/schema#>
                        PREFIX focup: <http://focu.io/schema/property#>
                        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        PREFIX schema: <http://schema.org/>
                        SELECT ?course_outline
                        WHERE
                        {{
                        ?course rdf:type focu:Course.
                        ?course focup:belongs_to "{course_name}".
                        ?course npg:number {course_number} .
                        ?course focup:has_outline ?course_outline.
                        }}"""
                        
        myobj = {'query': spql_query}
        x = requests.post(url, data = myobj)    
        desc = json.loads(x.text)['results']['bindings'][0]['course_outline']['value']

        #print(desc)
        dispatcher.utter_message(text=desc)
        #dispatcher.utter_message(text=message)


        return []



class ActionGetDept(Action):

    def name(self) -> Text:
        return "action_department_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = tracker.latest_message.get('text')
        messageArray = message.split(' ')


        url = 'http://localhost:3030/project/query'

        spql_query = f"""PREFIX dc: <http://purl.org/dc/elements/1.1/>
                        PREFIX np: <http://www.nanopub.org/nschema#>
                        PREFIX npg: <http://ns.nature.com/terms/>
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX focu: <http://focu.io/schema#>
                        PREFIX focup: <http://focu.io/schema/property#>
                        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        PREFIX schema: <http://schema.org/>
                        SELECT DISTINCT ?course_subject
                        WHERE
                        {{
                        ?course rdf:type focu:Course.
                        ?course focup:belongs_to ?course_subject .
                        ?course schema:isPartOf "{' '.join(messageArray[5:len(messageArray)-1])}".
                        }}"""
                        
        myobj = {'query': spql_query}
        x = requests.post(url, data = myobj)
        #print(x.text)    
        courselist = json.loads(x.text)['results']['bindings']
        courses = ''
        for course_detail in courselist:
            courses += course_detail['course_subject']['value'] +'\n'
                
        dispatcher.utter_message(text=courses)
        

        return []

class ActionGetGradCourses(Action):

    def name(self) -> Text:
        return "action_graduate_courses_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = tracker.latest_message.get('text')
        messageArray = message.split(' ')


        url = 'http://localhost:3030/project/query'

        spql_query = f"""PREFIX dc: <http://purl.org/dc/elements/1.1/>
                        PREFIX np: <http://www.nanopub.org/nschema#>
                        PREFIX npg: <http://ns.nature.com/terms/>
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX focu: <http://focu.io/schema#>
                        PREFIX focup: <http://focu.io/schema/property#>
                        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        PREFIX schema: <http://schema.org/>
                        SELECT ?course_name
                        WHERE
                        {{
                        ?course rdf:type focu:Course .
                        ?course focup:has_level "GRAD" .
                        ?course schema:isPartOf "{' '.join(messageArray[6:len(messageArray)-1])}" .
                        ?course foaf:name ?course_name .
                        }}"""
                        
        myobj = {'query': spql_query}
        x = requests.post(url, data = myobj)
        #print(x.text)    
        courselist = json.loads(x.text)['results']['bindings']
        courses = ''
        for course_detail in courselist:
            courses += course_detail['course_name']['value'] +'\n'
                
        dispatcher.utter_message(text=courses)
        

        return []





