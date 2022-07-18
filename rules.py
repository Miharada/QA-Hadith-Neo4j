import re
import pandas as pd

def notEmpty(listword):
  if(len(listword)>0):
    return True
  return False

def rules(text, showpendapat=False):
  Qpendapat=colPendapat=""
  if(notEmpty(re.findall(r"(?<=\bshow\s)(\w+)", text)) and notEmpty(re.findall(r"(?<=\bmention\s)(\w+)", text)) and text.split()[-1]=="matn"):
    topic = re.findall(r"(?<=\bmention\s)(\w+)",text)[0]
    if showpendapat:
      Qpendapat=",(m)-[:COMMENT_ABOUT_HADITH]->(p:Pendapat)"
      colPendapat=",p.pendapat AS Pendapat"
    query = r'''MATCH (b:Book)<-[:FROM_BOOK]-(m:Matn)-[:NARRATED_BY]->(s:Sanad){} 
    WHERE toLower(m.matn) =~ '(?i).*\\b{} \\b.*' 
    RETURN b.book AS Book, m.number AS Number, m.matn AS Matn, s.name AS Sanad{}'''.format(Qpendapat,topic,colPendapat)

  elif(notEmpty(re.findall(r"(?<=\bshow\s)(\w+)", text)) and notEmpty(re.findall(r"(?<=\bnarrated by\s)(\w+)", text))):
    topic = re.findall(r"(?<=narrated by)(.*)(?=and)", text)
    if showpendapat:
      Qpendapat=",(m)-[:COMMENT_ABOUT_HADITH]->(p:Pendapat)"
      colPendapat=",p.pendapat AS Pendapat"
    query='''MATCH (b:Book)<-[:FROM_BOOK]-(m:Matn)-[:NARRATED_BY]->(s:Sanad){} 
    WHERE toLower(s.name) CONTAINS toLower(\'{}\') and toLower(m.matn) CONTAINS toLower(\'{}\') 
    RETURN s.name AS Sanad, b.book AS Book,m.number AS Number ,m.matn AS Matn{}'''.format(Qpendapat, topic[0].strip(), text.split()[-1], colPendapat)

  elif(re.search("show [a-zA-Z]+ hadith about [a-zA-Z]+ during|and [a-zA-Z]+", text)):
    topic = re.findall(r"\w+\s(?=\bduring\b|\band\b|\bor\b|\bwhile\b)", text) + re.findall(r"(?<=[\bor\b|\bduring\b|\band\b|\bwhile\b])\s\w+", text)
    query=r'''MATCH (b:Book)<-[:FROM_BOOK]-(m:Matn) 
    WHERE toLower(m.matn) =~ '(?i).*\\b{} \\b.*' AND toLower(m.matn) =~ '(?i).*\\b{} \\b.*' 
    RETURN b.book AS Book, m.number AS Number, m.matn AS Matn'''.format(topic[0].strip(), topic[-1].strip())
 
  elif(notEmpty(re.findall(r"(?<=\babout\s)(\w+)",text)) and ((text.split()[0]=="who") or text.split()[0]=="is")):
    print("AYOLAH MASUK")
    topic = re.findall(r"(?<=\babout\s)(\w+)",text)[0]
    keterangan = expwhr = ""
    if showpendapat:
      Qpendapat=",(m)-[:COMMENT_ABOUT_HADITH]->(p:Pendapat)"
      colPendapat=",p.pendapat AS Pendapat"
      expwhr = "OR toLower(p.pendapat) CONTAINS toLower('{}')".format(topic)
      keterangan = ", Pendapat"
    query = '''
    WITH toLower("{}") as seq1
    MATCH (a:Answer)-[:ANSWER_OF]->(q:Question)<-[:RELATED_WITH]-(m:Matn)
    {}
    WITH toInteger(apoc.text.levenshteinDistance(seq1,toLower(q.question))) as similarity, a.answer AS Answer, m.matn AS Matn, q.question AS Question, m.id as Number{}
    WHERE toLower(m.matn) CONTAINS toLower("{}") OR similarity < 20 {}
    RETURN Question, Answer, Matn, Number{}
    ORDER BY similarity ASC
    LIMIT 10
    '''.format(text, Qpendapat, colPendapat,  topic, expwhr ,keterangan)

  else:
    keterangan = ""
    if showpendapat:
      Qpendapat=",(m)-[:COMMENT_ABOUT_HADITH]->(p:Pendapat)"
      colPendapat=",p.pendapat AS Pendapat"
      keterangan = ", Pendapat"
    query = '''
    WITH toLower("{}") as seq1
    MATCH (a:Answer)-[:ANSWER_OF]->(q:Question)<-[:RELATED_WITH]-(m:Matn)
    {}
    WITH toInteger(apoc.text.levenshteinDistance(seq1,toLower(q.question))) as similarity, a.answer AS Answer, m.matn AS Matn, q.question AS Question, m.id as Number{}
    RETURN Question, Answer, Matn, Number{}
    ORDER BY similarity ASC
    LIMIT 10
    '''.format(text, Qpendapat, colPendapat, keterangan)
  return query

def text2cipher(text, conn, showpendapat=False):
    try:
        query_string = rules(text, showpendapat)
        print("APASUH",query_string)
        top_cat_df = pd.DataFrame([dict(_) for _ in conn.query(query_string)])
        try:
          top_cat_df= top_cat_df.sort_values(["similarity"], ascending=False)
        except:
          pass
        print("HEY", top_cat_df)
        return top_cat_df
    except Exception as e:
        print(e)
        print("Must Match The Rules")

def levenshteinDistance(text, conn):
  try:
    query_string = '''
    WITH \"{}\" as seq1
    MATCH (m:Matn) 
    RETURN toInteger(apoc.text.levenshteinDistance(seq1,toLower(m.matn))) as similarity, m.matn
    ORDER BY similarity DESC
    LIMIT 5
    '''.format(text)
    top_cat_df = pd.DataFrame([dict(_) for _ in conn.query(query_string)])
    return top_cat_df
  except:
    print("Wrong")



def addAhli(name, conn):
  query_name = "MERGE (a:Ahli{{name:\'{}\'}})".format(name)
  return conn.query(query_name)

def addPendapat(pendapat, conn):
  query_pendapat = "MERGE (k:Pendapat{{pendapat:\'{}\'}})".format(pendapat)
  return conn.query(query_pendapat)

def addRelationPendapatAhli(name, pendapat, conn):
  query = '''
  MATCH (n:Ahli), (k:Pendapat)
  WHERE n.name = \'{}\' AND k.pendapat = \'{}\'
  MERGE (n)-[r:GIVE_COMMENT]->(k)
  '''.format(name, pendapat)
  return conn.query(query)

def addRelationMatnPendapat(pendapat, matn, conn):
  # query  = '''
  # MATCH (n:Pendapat), (m:Matn)
  # WHERE n.pendapat = \'{}\' AND  apoc.text.replace(m.matn,'"','') = \"{}\"
  # MERGE (m)-[r:COMMENT_ABOUT_HADITH]->(n)
  # '''.format(pendapat, matn)

  query = '''
  MATCH (n:Pendapat), (m:Matn)
  WHERE n.pendapat = \'{}\' AND apoc.text.replace(m.matn, '"', "'") = "{}"
  MERGE (m)-[r:COMMENT_ABOUT_HADITH]->(n)
  '''.format(pendapat, matn.replace('"',"'"))
  return conn.query(query)

def addRelationExpert(name, pendapat, matn, conn):
  addAhli(name, conn)
  addPendapat(pendapat, conn)
  addRelationPendapatAhli(name, pendapat, conn)
  addRelationMatnPendapat(pendapat, matn, conn)
  return "Finish"

def inputPendapatAhli(name, pendapat, matn, conn):
  
  return addRelationExpert(name, pendapat, matn, conn)
