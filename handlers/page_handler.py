from flask import Flask, request, render_template


def render_input_page(args):
    S = args.get('S')
    R = args.get('R')
    return render_template('input.htm', S=S, R=R)


def render_initialisation_page():
    return render_template('initialise.htm')
