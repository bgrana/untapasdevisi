from flask import Flask, render_template

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update({
    "DEBUG": True
})

@app.route('/', methods=['GET'])
def get_index():
    username = "Username"
    return render_template("index.html", username=username)

if __name__ == '__main__':
    app.run()