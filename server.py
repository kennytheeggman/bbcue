from ui.component import Component
from ui.regex import RegexComponent
from flask import Flask, Response

app = Flask(__name__)


body = RegexComponent.from_folder("components/body", {})

slider = RegexComponent.from_folder("components/slider", {})

head = RegexComponent.from_folder("components/head", {})

s = slider({"value": 50})
s2 = slider({"value": 75})
h = head({})
b = body({"head": h, "body": str(s) + str(s2)})

@app.route("/")
def home():
    resp = Response(str(b))
    resp.headers['Content-Type'] = "text/html"
    return resp


for url, content in Component.files_response.items():

    app.add_url_rule(url, view_func=content)

if __name__ == "__main__":

    app.run()