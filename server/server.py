from ui.component import component
from flask import Flask


app = Flask(__name__)

@app.route("/")
def home():
    return str(body("body", {"header": header("header", {"msg": "testing"})}))



@component
def body(params):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    {params["header"]}
    <p>{params["id"]}</p>
    <i>{params["id"]}</i>
</body>
</html>
    """

@component
def header(params):
    return f"""
<h1>
    {params["msg"]} {params["id"]}
</h1>
    """