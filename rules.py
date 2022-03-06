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
    print("Masuk ke 1",topic)
    if showpendapat:
      Qpendapat="(p:Pendapat)--"
      colPendapat=",p.pendapat AS Pendapat"
    query = r"MATCH {}(b:Book)<-[:FROM_BOOK]-(m:Matn)-[:NARRATED_BY]->(s:Sanad) WHERE toLower(m.matn) =~ '(?i).*\\b{} \\b.*' RETURN b.book AS Book, m.number AS Number, m.matn AS Matn, s.name AS Sanad{}".format(Qpendapat,topic,colPendapat)

  elif(notEmpty(re.findall(r"(?<=\bshow\s)(\w+)", text)) and notEmpty(re.findall(r"(?<=\bnarrated by\s)(\w+)", text))):
    topic = re.findall(r"(?<=narrated by)(.*)(?=and)", text)
    print("Masuk ke 2", topic)
    if showpendapat:
      Qpendapat="(p:Pendapat)--"
      colPendapat=",p.pendapat AS Pendapat"
    query="MATCH {}(b:Book)<-[:FROM_BOOK]-(m:Matn)-[:NARRATED_BY]->(s:Sanad) WHERE toLower(s.name) CONTAINS toLower(\'{}\') and toLower(m.matn) CONTAINS toLower(\'{}\') RETURN s.name AS Sanad, b.book AS Book,m.number AS Number ,m.matn AS Matn{}".format(Qpendapat, topic[0].strip(), text.split()[-1], colPendapat)
    # print(query)
  
  elif(re.search("show [a-zA-Z]+ hadith about [a-zA-Z]+ during|and|or [a-zA-Z]+", text)):
    topic = re.findall(r"\w+\s(?=\bduring\b|\band\b|\bor\b|\bwhile\b)", text) + re.findall(r"(?<=[\bor\b|\bduring\b|\band\b|\bwhile\b])\s\w+", text)
    print("Masuk ke 3 ", topic)
    query=r"MATCH (b:Book)<-[:FROM_BOOK]-(m:Matn) WHERE toLower(m.matn) =~ '(?i).*\\b{} \\b.*' AND toLower(m.matn) =~ '(?i).*\\b{} \\b.*' RETURN b.book AS Book, m.number AS Number, m.matn AS Matn".format(topic[0].strip(), topic[-1].strip())
    
  elif(notEmpty(re.findall(r"is(\s+([a-zA-Z]+\s+)+)(halal|haram)\?", text))):
    topic = list(re.findall(r"is(\s+([a-zA-Z]+\s+)+)(halal|haram)\?", text)[0])
    print("Masuk 4", topic)
    if topic[-1] == "haram":
      topic[-1] = 'prohibited'
    elif topic[-1] == "halal":
      topic[-1] = 'lawful'
    query="MATCH (b:Book)<-[:FROM_BOOK]-(m:Matn) WHERE m.matn CONTAINS \'{}\' and m.matn CONTAINS \'{}\' RETURN b.book AS Book, m.number AS Number, m.matn AS Matn".format(topic[1].strip(), topic[-1])
  else:
    query = "WITH '{}' as seq1 MATCH (a:Answer)-[:ANSWER_OF]->(q:Question)<-[:RELATED_WITH]-(m:Matn) RETURN toInteger(apoc.text.jaroWinklerDistance(seq1,q.question)*100) as similarity, q.question, m.matn, a.answer ORDER BY similarity DESC".format(text)
  return query

def text2cipher(text, conn):
    try:
        query_string = rules(text)
        print("APASUH",query_string)
        top_cat_df = pd.DataFrame([dict(_) for _ in conn.query(query_string)])
        try:
          top_cat_df= top_cat_df.sort_values(["similarity"], ascending=False)
        except:
          pass
        print("HEY", top_cat_df)
        return top_cat_df
    except:
        print("Must Match The Rules")

def neojarowinkler(text, conn):
  try:
    query_string = '''
    WITH \"{}\" as seq1
    MATCH (m:Matn) 
    RETURN toInteger(apoc.text.jaroWinklerDistance(seq1,toLower(m.matn))*100) as similarity, m.matn
    ORDER BY similarity DESC
    LIMIT 5
    '''.format(text)
    top_cat_df = pd.DataFrame([dict(_) for _ in conn.query(query_string)])
    return top_cat_df
  except:
    print("Wrong")
