from flask import Flask, render_template, request, redirect, url_for, jsonify

import neo4jcon as neo
from rules import text2cipher, neojarowinkler
from IPython.display import HTML

app = Flask(__name__)
app.secret_key = "secret key"

uri = "neo4j+s://9209303b.databases.neo4j.io"
user = "neo4j"
pwd = "lGF8HuqTO2omc-egJm-8Koae9ZuqdM5MaeLCdVr2Rvo"

conn = neo.Neo4jConnection(uri=uri, user=user, pwd=pwd)
print(conn)
@app.route('/')
def home_page():
    return render_template('QA_Hadith.html')

@app.route('/', methods=['POST'])
def generateHadith():
    text = request.form['statement']
    df = text2cipher(text.lower(), conn)
    try:
        return render_template('QA_Hadith.html', statement=text, tableHadith=HTML(df.to_html(classes='table table-striped" id = "a_nice_table',
                                       index=False, border=0)), rules=False)
    except:
        return render_template('QA_Hadith.html', rules=True)

@app.route('/qahadithv2', methods=['POST'])
def generatehadithsimbased():
    text = request.form['statement']
    df = neojarowinkler(text.lower(), conn)
    try:
        return render_template('QA_v2.html', statement=text, tableHadith=HTML(df.to_html(classes='table table-striped" id = "a_nice_table',
                                       index=False, border=0)))
    except:
        return render_template('QA_v2.html')


@app.route('/expertpage')
def expertcomment():
    return render_template("ExpertPage.html")

@app.route('/qahadithv2')
def qahadith2():
    return render_template("QA_v2.html")

if __name__ == "__main__":
    app.run(debug=False)

#https://neo4j.com/developer/cypher/filtering-query-results/
#https://neo4j.com/developer/cypher/guide-build-a-recommendation-engine/
