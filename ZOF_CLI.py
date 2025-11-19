#!/usr/bin/env python3
"""
ZOF_CLI.py
Zero of Functions CLI - supports:
1. Bisection
2. Regula Falsi (False Position)
3. Secant
4. Newton-Raphson
5. Fixed Point Iteration
6. Modified Secant

Usage: run this file and follow the interactive menu.

Author: Julia (you can change)
Python tested: 3.10
"""

from math import *
import sys

def safe_eval(expr, x):
    """Evaluate user function expr at x in a safe-ish math context."""
    allowed = {k: globals().get(k) or __builtins__.get(k) for k in ['abs','min','max','pow']}
    # Provide math functions and constants:
    import math
    env = {name: getattr(math, name) for name in dir(math) if not name.startswith("__")}
    env.update({'x': x})
    # allow pow, abs etc.
    env.update({'abs': abs, 'pow': pow})
    try:
        return eval(expr, {"__builtins__": {}}, env)
    except Exception as e:
        raise ValueError(f"Error evaluating expression '{expr}' at x={x}: {e}")

def numeric_derivative(f_expr, x, h=1e-6):
    return (safe_eval(f_expr, x + h) - safe_eval(f_expr, x - h)) / (2*h)

def bisection(f_expr, a, b, tol=1e-6, maxiter=50):
    fa = safe_eval(f_expr, a)
    fb = safe_eval(f_expr, b)
    if fa * fb > 0:
        raise ValueError("f(a) and f(b) must have opposite signs for bisection.")
    history = []
    for k in range(1, maxiter+1):
        c = (a + b) / 2
        fc = safe_eval(f_expr, c)
        err = abs(b - a) / 2
        history.append((k, a, b, c, fc, err))
        if abs(fc) == 0 or err < tol:
            return c, abs(fc), k, history
        if fa * fc < 0:
            b = c
            fb = fc
        else:
            a = c
            fa = fc
    return (a+b)/2, abs(safe_eval(f_expr, (a+b)/2)), maxiter, history

def regula_falsi(f_expr, a, b, tol=1e-6, maxiter=50):
    fa = safe_eval(f_expr, a)
    fb = safe_eval(f_expr, b)
    if fa * fb > 0:
        raise ValueError("f(a) and f(b) must have opposite signs for Regula Falsi.")
    history = []
    for k in range(1, maxiter+1):
        c = (a*fb - b*fa) / (fb - fa)
        fc = safe_eval(f_expr, c)
        err = abs(fc)
        history.append((k, a, b, c, fc, err))
        if abs(fc) < tol:
            return c, abs(fc), k, history
        if fa * fc < 0:
            b = c
            fb = fc
        else:
            a = c
            fa = fc
    return c, abs(fc), maxiter, history

def secant(f_expr, x0, x1, tol=1e-6, maxiter=50):
    history = []
    f0 = safe_eval(f_expr, x0)
    f1 = safe_eval(f_expr, x1)
    for k in range(1, maxiter+1):
        if (f1 - f0) == 0:
            raise ZeroDivisionError("Zero division in secant method (f1 - f0 == 0).")
        x2 = x1 - f1*(x1 - x0)/(f1 - f0)
        f2 = safe_eval(f_expr, x2)
        err = abs(x2 - x1)
        history.append((k, x0, x1, x2, f2, err))
        if abs(f2) < tol or err < tol:
            return x2, abs(f2), k, history
        x0, f0 = x1, f1
        x1, f1 = x2, f2
    return x2, abs(f2), maxiter, history

def newton_raphson(f_expr, x0, tol=1e-6, maxiter=50):
    history = []
    x = x0
    for k in range(1, maxiter+1):
        fx = safe_eval(f_expr, x)
        dfx = numeric_derivative(f_expr, x)
        if dfx == 0:
            raise ZeroDivisionError("Zero derivative encountered in Newton-Raphson.")
        x_new = x - fx/dfx
        err = abs(x_new - x)
        history.append((k, x, fx, dfx, x_new, err))
        if abs(fx) < tol or err < tol:
            return x_new, abs(safe_eval(f_expr, x_new)), k, history
        x = x_new
    return x, abs(safe_eval(f_expr, x)), maxiter, history

def fixed_point(g_expr, x0, tol=1e-6, maxiter=50):
    history = []
    x = x0
    for k in range(1, maxiter+1):
        x_new = safe_eval(g_expr, x)
        err = abs(x_new - x)
        history.append((k, x, x_new, err))
        if err < tol:
            return x_new, err, k, history
        x = x_new
    return x, err, maxiter, history

def modified_secant(f_expr, x0, delta=1e-3, tol=1e-6, maxiter=50):
    history = []
    x = x0
    for k in range(1, maxiter+1):
        fx = safe_eval(f_expr, x)
        denom = safe_eval(f_expr, x + delta*x) - fx
        if denom == 0:
            raise ZeroDivisionError("Zero division in modified secant denominator.")
        x_new = x - (delta * x * fx) / denom
        err = abs(x_new - x)
        history.append((k, x, fx, x_new, err))
        if abs(fx) < tol or err < tol:
            return x_new, abs(safe_eval(f_expr, x_new)), k, history
        x = x_new
    return x, abs(safe_eval(f_expr, x)), maxiter, history

def print_history(method, history):
    print(f"\n--- Iteration history for {method} ---")
    for row in history:
        print(row)

def interactive_menu():
    print("Zero of Functions (ZOF) CLI")
    methods = {
        "1": ("Bisection", bisection),
        "2": ("Regula Falsi", regula_falsi),
        "3": ("Secant", secant),
        "4": ("Newton-Raphson", newton_raphson),
        "5": ("Fixed Point", fixed_point),
        "6": ("Modified Secant", modified_secant)
    }
    while True:
        print("\nSelect method:")
        for k,v in methods.items():
            print(f"{k}. {v[0]}")
        print("q. Quit")
        choice = input("Enter choice: ").strip()
        if choice == 'q':
            print("Exiting.")
            sys.exit(0)
        if choice not in methods:
            print("Invalid choice. Try again.")
            continue
        name, func = methods[choice]
        print(f"Selected: {name}")
        f_expr = input("Enter f(x) as a Python expression (use math functions, variable 'x', e.g. x**3 - 2*x - 5):\n f(x) = ").strip()
        tol = float(input("Tolerance (e.g. 1e-6): ") or 1e-6)
        maxiter = int(input("Maximum iterations (e.g. 50): ") or 50)
        try:
            if choice == "1" or choice == "2":
                a = float(input("Left bracket a: "))
                b = float(input("Right bracket b: "))
                root, ferr, iters, history = func(f_expr, a, b, tol, maxiter)
                print(f"\nEstimated root: {root}\nf(root) ~ {ferr}\nIterations: {iters}")
                print_history(name, history)
            elif choice == "3":
                x0 = float(input("x0: "))
                x1 = float(input("x1: "))
                root, ferr, iters, history = func(f_expr, x0, x1, tol, maxiter)
                print(f"\nEstimated root: {root}\nf(root) ~ {ferr}\nIterations: {iters}")
                print_history(name, history)
            elif choice == "4":
                x0 = float(input("Initial guess x0: "))
                root, ferr, iters, history = func(f_expr, x0, tol, maxiter)
                print(f"\nEstimated root: {root}\nf(root) ~ {ferr}\nIterations: {iters}")
                print_history(name, history)
            elif choice == "5":
                print("NOTE: For Fixed Point, you must provide g(x) such that x=g(x).")
                g_expr = input("Enter g(x): ").strip()
                x0 = float(input("Initial guess x0: "))
                root, err, iters, history = func(g_expr, x0, tol, maxiter)
                print(f"\nEstimated fixed point: {root}\nFinal error ~ {err}\nIterations: {iters}")
                print_history(name, history)
            elif choice == "6":
                x0 = float(input("Initial guess x0: "))
                delta = float(input("Delta (small fraction, e.g. 1e-3): ") or 1e-3)
                root, ferr, iters, history = func(f_expr, x0, delta, tol, maxiter)
                print(f"\nEstimated root: {root}\nf(root) ~ {ferr}\nIterations: {iters}")
                print_history(name, history)
        except Exception as e:
            print("Error during computation:", e)

if __name__ == "__main__":
    interactive_menu()
