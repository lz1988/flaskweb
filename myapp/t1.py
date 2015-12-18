from t import init_db
#encoding:utf-8
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
init_db()
