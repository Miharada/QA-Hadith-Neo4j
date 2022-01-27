from flask import Flask, render_template, request, redirect, url_for, jsonify

import neo4jcon as neo
from rules import text2cipher
from IPython.display import HTML

app = Flask(__name__)
app.secret_key = "secret key"

uri = "bolt://34.201.60.59:7687"
user = "neo4j"
pwd = "hilltops-cares-relations"

conn = neo.Neo4jConnection(uri=uri, user=user, pwd=pwd)
print(conn)
@app.route('/')
def home_page():
    return render_template('QA_Hadith.html')

@app.route('/', methods=['POST'])
def generateHadith():
    text = request.form['statement']
    df = text2cipher(text.lower(), conn)
    print(HTML(df.to_html()))
    return render_template('QA_Hadith.html', statement=text, tableHadith=HTML(df.to_html(classes='table table-striped" id = "a_nice_table',
                                       index=False, border=0)))


@app.route('/expertpage')
def expertcomment():
    return render_template("ExpertPage.html")

if __name__ == "__main__":
    app.run(debug=False)

#https://neo4j.com/developer/cypher/filtering-query-results/
#https://neo4j.com/developer/cypher/guide-build-a-recommendation-engine/
