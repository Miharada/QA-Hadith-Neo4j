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
    query = r"MATCH {}(m:Matn)-[:NARRATED_BY]->(s:Sanad) WHERE toLower(m.matn) =~ '(?i).*\\b{} \\b.*' RETURN m.matn AS Matn, s.name AS Name{}".format(Qpendapat,topic,colPendapat)

  elif(notEmpty(re.findall(r"(?<=\bshow\s)(\w+)", text)) and notEmpty(re.findall(r"(?<=\bnarrated by\s)(\w+)", text))):
    topic = re.findall(r"(?<=narrated by)(.*)(?=and)", text)
    print("Masuk ke 2", topic)
    if showpendapat:
      Qpendapat="(p:Pendapat)--"
      colPendapat=",p.pendapat AS Pendapat"
    query="MATCH {}(m:Matn)-[:NARRATED_BY]->(s:Sanad) WHERE toLower(s.name) CONTAINS toLower(\'{}\') and toLower(m.matn) CONTAINS toLower(\'{}\') RETURN s.name AS Name, m.matn AS Matn{}".format(Qpendapat, topic[0].strip(), text.split()[-1], colPendapat)
    # print(query)
  
  elif(re.search("show [a-zA-Z]+ hadith about [a-zA-Z]+ during|and|or [a-zA-Z]+", text)):
    topic = re.findall(r"\w+\s(?=\bduring\b|\band\b|\bor\b)", text) + re.findall(r"(?<=[\bor\b|\bduring\b|\band\b])\s\w+", text)
    print("Masuk ke 3 ", topic)
    query=r"MATCH (m:Matn) WHERE toLower(m.matn) =~ '(?i).*\\b{} \\b.*' AND toLower(m.matn) =~ '(?i).*\\b{} \\b.*' RETURN m.matn AS Matn".format(topic[0].strip(), topic[-1].strip())
    
  elif(notEmpty(re.findall(r"is(\s+([a-zA-Z]+\s+)+)(halal|haram)\?", text))):
    topic = list(re.findall(r"is(\s+([a-zA-Z]+\s+)+)(halal|haram)\?", text)[0])
    print("Masuk 4", topic)
    if topic[-1] == "haram":
      topic[-1] = 'prohibited'
    query="MATCH (m:Matn) WHERE m.matn CONTAINS \'{}\' and m.matn CONTAINS \'{}\' RETURN m.matn AS Matn".format(topic[1].strip(), topic[-1])

  return query

def text2cipher(text, conn):
    try:
        query_string = rules(text)
        print("APASUH",query_string)
        top_cat_df = pd.DataFrame([dict(_) for _ in conn.query(query_string)])
        return top_cat_df
    except:
        print("Must Match The Rules")
