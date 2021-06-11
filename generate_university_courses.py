import pandas
import os
import urllib.parse
from rdflib import Namespace, Graph, RDF, RDFS, URIRef, Literal, BNode
from rdflib.namespace import FOAF, DC, XSD, OWL


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

Concordia_University = URIRef(focu.Concordia_University + '/')
Course = focu.Course
Lecture = focu.Lecture
Lab  =focu.Lab
Topic = focu.Topic

def generate_courses():
    catalogs_csv = pandas.read_csv("https://opendata.concordia.ca/datasets/sis/CU_SR_OPEN_DATA_CATALOG.csv",
                                   engine="python")
    descriptions_csv = pandas.read_csv("https://opendata.concordia.ca/datasets/sis/CU_SR_OPEN_DATA_CATALOG_DESC.csv",
                                       engine="python")
    faculty_csv = pandas.read_csv("https://opendata.concordia.ca/datasets/sis/CU_SR_OPEN_DATA_SCHED.csv",
                                       engine="python")
    faculty_csv = faculty_csv.loc[:, ['Course ID', 'Faculty Descr']]
    #print(faculty_csv.head())
    courses_dataframe_temp  = catalogs_csv.merge(descriptions_csv, on='Course ID' , how='left')
    courses_dataframe = courses_dataframe_temp.merge(faculty_csv, on='Course ID',  how='left')
    #courses_dataframe.drop(
    #    courses_dataframe[~(courses_dataframe["Component Descr"] == "Lecture")].index,
    #    inplace=True)
    courses_dataframe.drop_duplicates(subset='Course ID', inplace=True)
    courses_dataframe.drop(
        ['Class Units', 'Component Code', 'Component Descr', 'Pre Requisite Description',
         'Equivalent Courses' ], axis=1,
        inplace=True)
    courses_dataframe.rename(
        columns={'Subject': 'Course Subject', 'Catalog': 'Course Number', 'Long Title': 'Course Name',
                 'Descr': 'Course Description', 'Career': 'Level'}, inplace=True)
    courses_dataframe.to_csv(r'courses_list.csv', header=True, index=False)


def add_university():
    
    graph.add((Concordia_University, RDF.type, focu.University))
    graph.add((Concordia_University, RDFS.comment, Literal("Concordia University is a university.", lang="en")))
    graph.add((Concordia_University, RDFS.seeAlso, URIRef("http://www.concordia.ca/")))
    graph.add((Concordia_University, OWL.sameAs, URIRef(dbr.Concordia_University)))
    graph.add((Concordia_University, RDFS.label, Literal("Concordia University", lang="en")))
    

def add_courses():
    course_list = pandas.read_csv('courses_list.csv')
    for i in range(len(course_list)):
        course_number = str(course_list.iloc[i]['Course Number'])
        course_name = course_list.iloc[i]['Course Name']
        course_id = course_list.iloc[i]['Course ID']
        course_description = course_list.iloc[i]['Course Description']
        course_subject = course_list.iloc[i]['Course Subject']
        course_level = course_list.iloc[i]['Level']
        course_faculty_desc = course_list.iloc[i]['Faculty Descr']
        #course = focu[str(course_id) + '/']
        course = focudata[str(course_subject +'_'+ course_number) + '/']
        graph.add((course, RDF.type, focu.Course))
        graph.add((course,focup.belongs_to, Literal(course_subject, datatype=XSD.string)))
        graph.add((course, RDFS.label, Literal(course_number, lang="en")))
        graph.add((course, RDFS.comment,
                   Literal(course_number + " is a part of " + course_subject + ".", lang="en")))
        graph.add((course, RDFS.seeAlso,
                   URIRef("https://opendata.concordia.ca/datasets/sis/CU_SR_OPEN_DATA_CATALOG.csv")))
        graph.add((course, FOAF.name, Literal(course_name, datatype=XSD.string)))
        graph.add((course, DC.identifier, Literal(str(course_id), datatype=XSD.string)))
        graph.add((course, npg.number, Literal(course_number, datatype=XSD.integer)))
        graph.add((course, focup.has_level, Literal(course_level, datatype=XSD.string)))
        graph.add((course, DC.description, Literal(course_description, datatype=XSD.string)))
        graph.add((course, schema.isPartOf,  Literal(course_faculty_desc, datatype=XSD.string)))
        graph.add((course, schema.isPartOf,  focudata['Concordia_University/']))
        if str(course_subject +'_'+ course_number) == 'COMP_6741' or str(course_subject +'_'+ course_number) == 'COMP_474':
            graph.add((course, focup.has_outline, URIRef('file:///'+os.getcwd().replace('\\','/')+'/database/COMP6741syllabus.pdf') ))
        if str(course_subject +'_'+ course_number) == 'COMP_6321':
            graph.add((course, focup.has_outline, URIRef('file:///'+os.getcwd().replace('\\','/')+'/database/COMP6321syllabus.pdf') ))

    

def save_graph():
    graph.serialize(destination='graph.nt', format='nt')

generate_courses()
add_university()
add_courses()
save_graph()
