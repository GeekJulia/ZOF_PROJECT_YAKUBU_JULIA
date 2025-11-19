from flask import Flask, render_template, request, jsonify
from math import *
import math

app = Flask(__name__)

# Reuse the safe eval and numerical functions (same logic as CLI)
def safe_eval(expr, x):
    import math
    env = {name: getattr(math, name) for name in dir(math) if not name.startswith("__")}
    env.update({'x': x, 'abs': abs, 'pow': pow})
    try:
        return eval(expr, {"__builtins__": {}}, env)
    except Exception as e:
        raise ValueError(f"Error evaluating expression '{expr}' at x={x}: {e}")

def numeric_derivative(f_expr, x, h=1e-6):
    return (safe_eval(f_expr, x + h) - safe_eval(f_expr, x - h)) / (2*h)

# Implementations (same as CLI but returning serializable history)
def bisection(f_expr, a, b, tol=1e-6, maxiter=50):
    fa = safe_eval(f_expr, a); fb = safe_eval(f_expr, b)
    if fa * fb > 0:
        return {"error": "f(a) and f(b) must have opposite signs."}
    history = []
    for k in range(1, maxiter+1):
        c = (a + b) / 2
        fc = safe_eval(f_expr, c)
        err = abs(b - a) / 2
        history.append({"iter":k,"a":a,"b":b,"c":c,"f(c)":fc,"err":err})
        if abs(fc) == 0 or err < tol:
            return {"root":c,"f(root)":abs(fc),"iters":k,"history":history}
        if fa * fc < 0:
            b = c; fb = fc
        else:
            a = c; fa = fc
    return {"root":(a+b)/2,"f(root)":abs(safe_eval(f_expr,(a+b)/2)),"iters":maxiter,"history":history}

def regula_falsi(f_expr, a, b, tol=1e-6, maxiter=50):
    fa = safe_eval(f_expr, a); fb = safe_eval(f_expr, b)
    if fa * fb > 0:
        return {"error": "f(a) and f(b) must have opposite signs."}
    history = []
    for k in range(1, maxiter+1):
        c = (a*fb - b*fa) / (fb - fa)
        fc = safe_eval(f_expr, c)
        err = abs(fc)
        history.append({"iter":k,"a":a,"b":b,"c":c,"f(c)":fc,"err":err})
        if abs(fc) < tol:
            return {"root":c,"f(root)":abs(fc),"iters":k,"history":history}
        if fa * fc < 0:
            b = c; fb = fc
        else:
            a = c; fa = fc
    return {"root":c,"f(root)":abs(fc),"iters":maxiter,"history":history}

def secant(f_expr, x0, x1, tol=1e-6, maxiter=50):
    history = []
    f0 = safe_eval(f_expr, x0)
    f1 = safe_eval(f_expr, x1)
    for k in range(1, maxiter+1):
        if (f1 - f0) == 0:
            return {"error":"Zero division in secant (f1 - f0 == 0)."}
        x2 = x1 - f1*(x1 - x0)/(f1 - f0)
        f2 = safe_eval(f_expr, x2)
        err = abs(x2 - x1)
        history.append({"iter":k,"x0":x0,"x1":x1,"x2":x2,"f(x2)":f2,"err":err})
        if abs(f2) < tol or err < tol:
            return {"root":x2,"f(root)":abs(f2),"iters":k,"history":history}
        x0, f0 = x1, f1
        x1, f1 = x2, f2
    return {"root":x2,"f(root)":abs(f2),"iters":maxiter,"history":history}

def newton_raphson(f_expr, x0, tol=1e-6, maxiter=50):
    history = []
    x = x0
    for k in range(1, maxiter+1):
        fx = safe_eval(f_expr, x)
        dfx = numeric_derivative(f_expr, x)
        if dfx == 0:
            return {"error":"Zero derivative encountered."}
        x_new = x - fx/dfx
        err = abs(x_new - x)
        history.append({"iter":k,"x":x,"f(x)":fx,"f'(x)":dfx,"x_new":x_new,"err":err})
        if abs(fx) < tol or err < tol:
            return {"root":x_new,"f(root)":abs(safe_eval(f_expr,x_new)),"iters":k,"history":history}
        x = x_new
    return {"root":x,"f(root)":abs(safe_eval(f_expr,x)),"iters":maxiter,"history":history}

def fixed_point(g_expr, x0, tol=1e-6, maxiter=50):
    history = []
    x = x0
    for k in range(1, maxiter+1):
        x_new = safe_eval(g_expr, x)
        err = abs(x_new - x)
        history.append({"iter":k,"x":x,"g(x)":x_new,"err":err})
        if err < tol:
            return {"root":x_new,"err":err,"iters":k,"history":history}
        x = x_new
    return {"root":x,"err":err,"iters":maxiter,"history":history}

def modified_secant(f_expr, x0, delta=1e-3, tol=1e-6, maxiter=50):
    history = []
    x = x0
    for k in range(1, maxiter+1):
        fx = safe_eval(f_expr, x)
        denom = safe_eval(f_expr, x + delta*x) - fx
        if denom == 0:
            return {"error":"Zero division in modified secant denominator."}
        x_new = x - (delta * x * fx) / denom
        err = abs(x_new - x)
        history.append({"iter":k,"x":x,"f(x)":fx,"x_new":x_new,"err":err})
        if abs(fx) < tol or err < tol:
            return {"root":x_new,"f(root)":abs(safe_eval(f_expr,x_new)),"iters":k,"history":history}
        x = x_new
    return {"root":x,"f(root)":abs(safe_eval(f_expr,x)),"iters":maxiter,"history":history}

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/compute", methods=["POST"])
def compute():
    data = request.form
    method = data.get("method")
    f_expr = data.get("f_expr", "")
    g_expr = data.get("g_expr", "")
    tol = float(data.get("tol", 1e-6))
    maxiter = int(data.get("maxiter", 50))
    try:
        if method in ["bisection", "regula_falsi"]:
            a = float(data.get("a", 0))
            b = float(data.get("b", 1))
            if method == "bisection":
                res = bisection(f_expr, a, b, tol, maxiter)
            else:
                res = regula_falsi(f_expr, a, b, tol, maxiter)
        elif method == "secant":
            x0 = float(data.get("x0", 0))
            x1 = float(data.get("x1", 1))
            res = secant(f_expr, x0, x1, tol, maxiter)
        elif method == "newton":
            x0 = float(data.get("x0", 0))
            res = newton_raphson(f_expr, x0, tol, maxiter)
        elif method == "fixed_point":
            x0 = float(data.get("x0", 0))
            res = fixed_point(g_expr, x0, tol, maxiter)
        elif method == "modified_secant":
            x0 = float(data.get("x0", 0))
            delta = float(data.get("delta", 1e-3))
            res = modified_secant(f_expr, x0, delta, tol, maxiter)
        else:
            res = {"error": "Unknown method"}
    except Exception as e:
        res = {"error": str(e)}
    return render_template("index.html", result=res, form=data)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
