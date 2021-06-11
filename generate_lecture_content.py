import pandas
import os
import urllib.parse
from rdflib import Namespace, Graph, RDF, RDFS, URIRef, Literal, BNode
from rdflib.namespace import FOAF, DC, XSD, OWL
import urllib
import natsort

def encode_url(url):
    return urllib.parse.quote_plus(url)


prefix_dict = {"dbo": "http://dbpedia.org/ontology/",
                   "dbr": "http://dbpedia.org/resource/",
                   "focu": "http://focu.io/schema#",
                   "focup": "http://focu.io/schema/property#",
                   "focudata": "http://focu.io/data#",
                   "schema": "http://schema.org/",
                   "npg": "http://ns.nature.com/terms/"}

dbo = Namespace(prefix_dict.get("dbo"))
dbr = Namespace(prefix_dict.get("dbr"))
focu = Namespace(prefix_dict.get("focu"))
focup = Namespace(prefix_dict.get("focup"))
focudata = Namespace(prefix_dict.get("focudata"))
schema = Namespace(prefix_dict.get("schema"))
npg = Namespace(prefix_dict.get("npg"))

graph = Graph()

graph.bind('dbo', dbo)
graph.bind('dbr', dbr)
graph.bind('focu', focu)
graph.bind('focup', focup)
graph.bind('focudata', focudata)
graph.bind('schema', schema)
graph.bind('owl', OWL)
graph.bind('foaf', FOAF)
graph.bind('dc', DC)
graph.bind('xsd', XSD)
graph.bind('npg', npg)


def add_content():
    component_dirs = []
    for (root,dirs,files) in os.walk(os.getcwd()+'\\database\\Concordia_University', topdown=True):
        #print (root)
        #print (dirs)
        #print (files)
        #print ('--------------------------------')

        if dirs:
            component_dirs = natsort.natsorted(dirs)
       
        if files:
            rootArray = root.split('\\')
            component_name = rootArray[len(rootArray) - 1]
            component_type = rootArray[len(rootArray) - 2]
            #print('component_dirs ',component_dirs)
            course = rootArray[len(rootArray) - 3]
            component_number = component_dirs.index(component_name) + 1
            unique_component_id  = rootArray[len(rootArray) - 3] + component_type + str(component_number)
            component = focudata[unique_component_id + '/']
            if component_type == 'Lab':
                graph.add((component, RDF.type, focu.Lab))
                parent_lecture_id = rootArray[len(rootArray) - 3] + 'Lecture' + str(component_dirs.index(component_name) + 1)
                graph.add((component, RDFS.subClassOf, focudata[parent_lecture_id + '/']))
            if component_type == 'Lecture' :
                graph.add((component, RDF.type, focu.Lecture))
                graph.add((component, focup.belongs_to, focudata[course + '/']))
            graph.add((component, FOAF.name, Literal(component_name,  datatype=XSD.string) ))
            graph.add((component, RDFS.comment,Literal(component_name + " is a part of " + course + ".", lang="en")))
            graph.add((component, npg.number, Literal(component_number, datatype=XSD.integer)))
            
            file_uri = root.replace('\\','/')
            if len(files) > 0 and "slide" in files[0]:
                graph.add((component, focup.includes_slides , URIRef('file:///'+file_uri+'/'+files[0]) ) )
            if len(files) > 0 and ("lab" in files[0] or "Lab" in files[0]):
                graph.add((component, focup.includes_slides , URIRef('file:///'+file_uri+'/'+files[0]) ) )
            if len(files) > 1 and "worksheet" in files[1]:
                graph.add((component, focup.includes_worksheet , URIRef('file:///'+file_uri+'/'+files[1]) ) )

                

def save_graph():
    graph.serialize(destination='graph_content.ttl', format='ttl')

add_content()
save_graph()