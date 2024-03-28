from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        summoner_name = request.form['summoner_name']
        tagline = request.form['tagline']
        region = request.form['region']
        print(f"The user entered {summoner_name} as their summoner, the tagline is {tagline}, and the region is {region}")
        return render_template('homepage.html')
    else:
        return render_template('homepage.html')


