# -*-coding:utf8;-*-
import sqlite3
from datetime import datetime
import ftputil
import os


server = os.environ.get('FTP_SERVER')
user = os.environ.get('FTP_USER')
password = os.environ.get('FTP_PASSWORD')
ftp = ftputil.FTPHost(server, user, password)
ftp.download("/projects/xampp/xampp.db", "xampp.db")
date = datetime.now()
conn = sqlite3.connect('xampp.db')
cursor = conn.cursor()


def need_update(release):
    check = cursor.execute(
        "SELECT COUNT(*) from info WHERE release = ? LIMIT 1", (release,)).fetchone()
    return not bool(check[0])


def version_exists(version):
    check = cursor.execute(
        "SELECT COUNT(*) from info WHERE version = ? LIMIT 1", (version,)).fetchone()
    return check[0]


def get_latest_version():
    q = cursor.execute("SELECT MAX(version) FROM info").fetchone()
    return q[0]


def add_version(version):
    cursor.execute("INSERT INTO info (version, release, `update`) VALUES (?,?,?);",
                   (version, "-", date.strftime("%Y-%m-%d")))
    conn.commit()


def update_release(version, release):
    cursor.execute("UPDATE info SET release = ?, `update` = ? WHERE version = ?",
                   (release, date.strftime("%Y-%m-%d"), version))
    conn.commit()


def close():
    if conn:
        conn.close()
    ftp.upload_if_newer("xampp.db", "/projects/xampp/xampp.db")
