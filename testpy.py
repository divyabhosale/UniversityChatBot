from tika import parser
import requests
import spotlight
import os
import json


import spacy

message = "What is the lecture and lab content for Intelligent Systems?"
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

print(courses)
