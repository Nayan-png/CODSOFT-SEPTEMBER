from flask import Flask, render_template_string, request, redirect, url_for, flash
import math
import os
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'
HISTORY_FILE = 'history.json'

# ================= Helper Functions ================= #

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history[-10:], f)

history = load_history()

# ================= Calculator Functions ================= #

def basic_operations(num1, num2, operation):
    operations = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / y if y != 0 else None,
        '**': lambda x, y: x ** y,
        '%': lambda x, y: x % y if y != 0 else None,
        '//': lambda x, y: x // y if y != 0 else None
    }
    if operation in operations:
        result = operations[operation](num1, num2)
        if result is None:
            raise ZeroDivisionError("Division by zero is not allowed!")
        return result
    else:
        raise ValueError("Invalid operation")

def scientific_operations(num, operation):
    operations = {
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'log': math.log10,
        'ln': math.log,
        'sqrt': math.sqrt,
        'exp': math.exp,
        'abs': abs,
        'ceil': math.ceil,
        'floor': math.floor,
        'factorial': lambda x: math.factorial(int(x)) if x >= 0 and x == int(x) else None
    }
    if operation in operations:
        result = operations[operation](num)
        if result is None:
            raise ValueError("Invalid input for factorial")
        return result
    else:
        raise ValueError("Invalid scientific operation")

def evaluate_expression(expression):
    safe_dict = {
        "__builtins__": {},
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'log': math.log10,
        'ln': math.log,
        'sqrt': math.sqrt,
        'exp': math.exp,
        'abs': abs,
        'ceil': math.ceil,
        'floor': math.floor,
        'pi': math.pi,
        'e': math.e,
        'pow': pow
    }
    return eval(expression, safe_dict)

# ================= Routes ================= #

@app.route('/', methods=['GET', 'POST'])
def home():
    global history
    result = None
    error = None

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        try:
            if form_type == 'basic':
                num1 = float(request.form.get('num1'))
                num2 = float(request.form.get('num2'))
                operation = request.form.get('operation')
                result = basic_operations(num1, num2, operation)
                expression = f"{num1} {operation} {num2}"

            elif form_type == 'scientific':
                num = float(request.form.get('num'))
                operation = request.form.get('operation')
                result = scientific_operations(num, operation)
                expression = f"{operation}({num})"

            elif form_type == 'expression':
                expression = request.form.get('expression')
                result = evaluate_expression(expression)

            history.append(f"{expression} = {result}")
            save_history(history)

        except Exception as e:
            error = str(e)

    template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Advanced Scientific Calculator</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 text-gray-800">
    <div class="container mx-auto p-4">
        <h1 class="text-3xl font-bold text-center mb-6">🔬 Advanced Scientific Calculator</h1>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-white p-4 rounded shadow">
                <h2 class="text-xl font-semibold mb-2">📋 Basic Calculator</h2>
                <form method="POST">
                    <input type="hidden" name="form_type" value="basic">
                    <input type="number" step="any" name="num1" placeholder="First number" class="border p-2 rounded w-full mb-2" required>
                    <select name="operation" class="border p-2 rounded w-full mb-2">
                        <option value="+">+</option>
                        <option value="-">-</option>
                        <option value="*">*</option>
                        <option value="/">/</option>
                        <option value="**">**</option>
                        <option value="%">%</option>
                        <option value="//">//</option>
                    </select>
                    <input type="number" step="any" name="num2" placeholder="Second number" class="border p-2 rounded w-full mb-2" required>
                    <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded">Calculate</button>
                </form>
            </div>

            <div class="bg-white p-4 rounded shadow">
                <h2 class="text-xl font-semibold mb-2">🔬 Scientific Calculator</h2>
                <form method="POST">
                    <input type="hidden" name="form_type" value="scientific">
                    <input type="number" step="any" name="num" placeholder="Number" class="border p-2 rounded w-full mb-2" required>
                    <input type="text" name="operation" placeholder="Operation (sin, cos, sqrt...)" class="border p-2 rounded w-full mb-2" required>
                    <button type="submit" class="bg-green-500 text-white px-4 py-2 rounded">Calculate</button>
                </form>
            </div>

            <div class="bg-white p-4 rounded shadow md:col-span-2">
                <h2 class="text-xl font-semibold mb-2">🧮 Expression Evaluator</h2>
                <form method="POST">
                    <input type="hidden" name="form_type" value="expression">
                    <input type="text" name="expression" placeholder="Enter expression (e.g., sin(pi/2))" class="border p-2 rounded w-full mb-2" required>
                    <button type="submit" class="bg-purple-500 text-white px-4 py-2 rounded">Evaluate</button>
                </form>
            </div>
        </div>

        {% if result is not none %}
        <div class="mt-6 bg-yellow-100 p-4 rounded shadow">
            <h3 class="text-lg font-semibold">✨ Result:</h3>
            <p class="text-lg">{{ result }}</p>
        </div>
        {% endif %}

        {% if error %}
        <div class="mt-6 bg-red-100 p-4 rounded shadow">
            <h3 class="text-lg font-semibold">❌ Error:</h3>
            <p class="text-lg">{{ error }}</p>
        </div>
        {% endif %}

        <div class="mt-6 bg-white p-4 rounded shadow">
            <h3 class="text-lg font-semibold mb-2">📚 History</h3>
            <ul class="list-disc pl-6">
                {% for item in history %}
                <li>{{ item }}</li>
                {% else %}
                <li>No history yet.</li>
                {% endfor %}
            </ul>
            <a href="{{ url_for('clear_history') }}" class="mt-2 inline-block bg-red-500 text-white px-4 py-2 rounded">Clear History</a>
        </div>

        <div class="mt-6 bg-white p-4 rounded shadow">
            <h3 class="text-lg font-semibold mb-2">📊 Mathematical Constants</h3>
            <ul class="list-disc pl-6">
                <li>π (pi) : {{ pi }}</li>
                <li>e      : {{ e }}</li>
                <li>τ (tau): {{ tau }}</li>
                <li>φ (phi): {{ phi }}</li>
                <li>√2     : {{ sqrt2 }}</li>
                <li>√3     : {{ sqrt3 }}</li>
            </ul>
        </div>

    </div>
    </body>
    </html>
    '''

    return render_template_string(template, history=history[::-1], result=result, error=error)

@app.route('/clear_history')
def clear_history():
    global history
    history = []
    save_history(history)
    flash('History cleared successfully!', 'success')
    return redirect(url_for('home'))

@app.context_processor
def inject_constants():
    return dict(pi=math.pi, e=math.e, tau=2*math.pi, phi=(1+math.sqrt(5))/2, sqrt2=math.sqrt(2), sqrt3=math.sqrt(3))

if __name__ == '__main__':
    app.run(debug=True)
