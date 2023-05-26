from ui.component import Component, component, class_file, instance_file
from flask import Flask
from uuid import uuid4

app = Flask(__name__)

@component
def body(props):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    {props["head"]}
</head>
<body>
    {props["body"]}
</body>
</html>
    """

@component
def slider(props):
    return f"""
<div id={props["id"]}>
<input type="range" min="1" max="100" value="{props["value"]}">
</div>
    """

@component
def header(props):
    return """
<script src="/script.js"></script>
<script src="/script1.js"></script>
    """

@class_file(slider, "/script.js")
def src():
    return """
console.log("test");
    """
@class_file(slider, "/script1.js")
def src2():
    return """
console.log("1");
    """

s = slider({"value": 100})
h = header({})
b = body({"head": h, "body": s})

@app.route("/")
def home():
    return str(b)

@instance_file(s, "/script.js")
def src3(props):
    return f"""
console.log("success! {props["id"]}");
    """

for url, content in Component.files.items():

    app.add_url_rule(url, view_func=content)