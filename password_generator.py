from flask import Flask, render_template_string, request, redirect, url_for
import secrets, json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ================= Simple Passphrase Generator ================= #
class SimplePassGen:
    def __init__(self):
        self.history_file = "pass_history.json"
        self.history = []
        self.load_history()
        self.word_list = [
            "apple","beach","chair","dance","eagle","flame","grace","house",
            "island","jungle","kite","lemon","magic","night","ocean","peace",
            "queen","river","storm","tower","umbrella","valley","wizard","youth",
            "bridge","castle","dream","forest","garden","harbor","journey","knight",
            "mountain","rainbow","sunset","treasure","village","wonder","crystal","phoenix"
        ]

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file,"r") as f:
                    self.history = json.load(f)
            except:
                self.history = []

    def save_history(self):
        with open(self.history_file,"w") as f:
            json.dump(self.history[-20:],f,indent=2)

    def generate_passphrase(self, words=4, sep="-", capitalize=True, add_number=True, add_symbol=False):
        selected = [secrets.choice(self.word_list).capitalize() if capitalize else secrets.choice(self.word_list) for _ in range(words)]
        phrase = sep.join(selected)
        if add_number:
            phrase += sep + str(secrets.randbelow(9000)+1000)
        if add_symbol:
            phrase += sep + secrets.choice("!@#$%^&*")
        self.history.append({"phrase": phrase, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        self.save_history()
        return phrase

generator = SimplePassGen()

# ================= Flask Routes ================= #
@app.route("/", methods=["GET","POST"])
def home():
    result = None
    error = None
    if request.method=="POST":
        try:
            words = int(request.form.get("words",4))
            sep = request.form.get("sep") or "-"
            capitalize = request.form.get("capitalize")=="on"
            add_number = request.form.get("add_number")=="on"
            add_symbol = request.form.get("add_symbol")=="on"
            result = generator.generate_passphrase(words, sep, capitalize, add_number, add_symbol)
        except Exception as e:
            error = str(e)

    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Passphrase Generator</title>
    <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50 p-6">
    <div class="max-w-xl mx-auto">
        <h1 class="text-3xl font-bold text-center mb-6">🔑 Simple Passphrase Generator</h1>
        <div class="bg-white p-6 rounded shadow">
            <form method="POST" class="space-y-3">
                <label>Number of Words:
                    <input type="number" name="words" min="2" max="10" value="4" class="border p-1 rounded w-full">
                </label>
                <label>Separator:
                    <input type="text" name="sep" value="-" class="border p-1 rounded w-full">
                </label>
                <label><input type="checkbox" name="capitalize" checked> Capitalize Words</label><br>
                <label><input type="checkbox" name="add_number" checked> Add Numbers</label><br>
                <label><input type="checkbox" name="add_symbol"> Add Symbol (!@#$%)</label><br>
                <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded w-full">Generate</button>
            </form>
        </div>

        {% if result %}
        <div class="mt-4 bg-green-100 p-4 rounded shadow">
            <h2 class="font-semibold">Generated Passphrase:</h2>
            <p class="break-all text-lg">{{ result }}</p>
        </div>
        {% endif %}

        <div class="mt-6 bg-white p-4 rounded shadow">
            <h2 class="font-semibold mb-2">History (Last 20)</h2>
            <ul class="list-disc pl-5">
            {% for entry in history[::-1] %}
                <li>{{ entry.time }} : {{ entry.phrase }}</li>
            {% else %}
                <li>No history yet.</li>
            {% endfor %}
            </ul>
            <a href="{{ url_for('clear_history') }}" class="mt-2 inline-block bg-red-600 text-white px-4 py-2 rounded">Clear History</a>
        </div>
        {% if error %}
        <div class="mt-4 bg-red-100 p-2 rounded">{{ error }}</div>
        {% endif %}
    </div>
    </body>
    </html>
    """
    return render_template_string(template, result=result, history=generator.history, error=error)

@app.route("/clear_history")
def clear_history():
    generator.history = []
    generator.save_history()
    return redirect(url_for("home"))

if __name__=="__main__":
    app.run(debug=True)
