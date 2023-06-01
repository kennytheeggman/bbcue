from ui.components import component_context
from flask import Flask, Response

app = Flask(__name__)

ctx = component_context.ComponentContext()

body = ctx.from_folder("components/body", {})
slider = ctx.from_folder("components/slider", {})
head = ctx.from_folder("components/head", {})

b = body(
    {
        "head": head({}),
        "body": str(slider({"value": 50})) + str(slider({"value": 75}))
    })


@app.route("/")
def home():
    resp = Response(str(b))
    resp.headers['Content-Type'] = "text/html"
    return resp


for url, content in ctx.files_responses.items():
    app.add_url_rule(url, view_func=content)

if __name__ == "__main__":
    app.run()
