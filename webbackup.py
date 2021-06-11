import os
import shutil
import sys
import tarfile
import hashlib
import smtplib
import ssl
import errno
import requests
from datetime import datetime
from ftplib import FTP, error_perm
import socket

# valtozok, egyebek
# mukodeshez szukseges valtozok
now = datetime.now()
date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
path = "/home/backup_archive/%s" % date_time
adatbazisok = ['dbname']
# az eppen aktualis szerveren talalhato menteni szukseges adatbazisok
adatb = "/home/backup_archive/" + date_time + "/adatbazisok/"

szervernev = socket.getfqdn()

# emailhez szukseges valtozok
sender_email = "XXX"  # kuldo e-mail cime
sender_password = "YYY"  # kuldo jelszava
receiver_email = "ZZZ"  # Kinek menjen az e-mail?

# ftphez szukseges valtozok
ftp_host = 'localhost'
ftp_port = portnumber
ftp_username = ''  # az ftp szerveren a felhasznalo neve
ftp_password = ''  # ugyanazon felhasznalo jelszava
ftp_path = "/home/backup_archive/"

# adatbazis hasznalatahoz szukseges valtozok
db_username = "yee"
db_password = "haw"

# /var/www meretenek megallapitasa
print("A /var/www meretenek megallapitasa, valamint a /home eleres szabad hely ellenorzese tortenik...")

try:
    ftp = FTP()
    ftp.connect(ftp_host, ftp_port)
    print("jok vagyunk, mukodik az FTP")
    ftp.quit()
except Exception as e:
    print(e)
    message = """Subject: """ + szervernev + """ - sikertelen backup

        A script nem tudott tovabb haladni, mert a backup szerveren nem elerheto az FTP.
        """

    with smtplib.SMTP_SSL("mailserver", 465, ssl.create_default_context()) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message)
    exit()


def size(varwww='/var/www'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(varwww):
        for i in filenames:
            fajlnevek = os.path.join(dirpath, i)
            total_size += os.path.getsize(fajlnevek)
    return total_size


varwww_size = size() / (1024 * 1024)

print("A /var/www mappa merete: " + str(int(round(varwww_size, 2))) + " MB, a homeon pedig " + str(
    int(round(shutil.disk_usage("/home/").free / (1024 * 1024)))) + " MB Szabad hely van")

letitbeknown = "letitbeknown.txt"
f = requests.get(letitbeknown)


if shutil.disk_usage("/home/").free < size():
    print("Nem tudunk tovabb haladni, mert keves a hely")
    message = """Subject: """ + szervernev + """ - sikertelen backup
    
    A script nem tudott tovabb haladni, mert elfogyott a hely a forras szerveren.
    """

    with smtplib.SMTP_SSL("mailserver", 465, ssl.create_default_context()) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message)
    exit()


if int(f.text) < size():
    print("Nem tudunk tovabb haladni, mert keves a hely")
    message = """Subject: """ + szervernev + """ - sikertelen backup

    A script nem tudott tovabb haladni, mert nincs eleg hely backup szerveren.
    """

    with smtplib.SMTP_SSL("mailserver", 465, ssl.create_default_context()) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message)
    exit()

# /home/backup_archive/__DATUM__ mappa letrehozasa
if os.path.isdir("/home/backup_archive"):
    print("A home/backup_archive mappa letezik, haladunk tovabb")
else:
    print("A home/backup_archive nem letezik, megprobaljuk letrehozni")
    try:
        os.mkdir("/home/backup_archive", 0o777)
    except OSError:
        print("A mappa letrehozasa nem sikerult (%s), a program kilep." % "/home/backup_archive")
        message = """Subject: """ + szervernev + """ - sikertelen backup
        
        A script nem tudott backupot kesziteni, mert a /home/backup_archive mappa nem tudott letrejonni
        """

        with smtplib.SMTP_SSL("mailserver", 465, ssl.create_default_context()) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message)
        exit()

    else:
        print("Sikerult a kovetkezo mappa letrehozasa: %s" % "/home/backup_archive")

try:
    os.mkdir(path, 0o777)
except OSError:
    print("A mappa letrehozasa nem sikerult, a program kilep.")
    message = """Subject: """ + szervernev + """ - sikertelen backup
        
        A script nem tudott backupot kesziteni, mert a /home/backup_archive/""" \
              + date_time + """ mappa nem tudott letrejonni
        """

    with smtplib.SMTP_SSL("mailserver", 465, ssl.create_default_context()) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message)
    exit()


else:
    print("Sikerult a kovetkezo mappa letrehozasa: %s " % path)

# csomagolas, es meret ellenorzes
print("A csomagolas folyamatban van a kovetkezo eleresre: %s" % "/home/backup_archive/" + date_time + "/www.tar.gz")
tar = tarfile.open("/home/backup_archive/" + date_time + "/www.tar.gz", "w:gz")
os.chdir("/var/www")
for name in os.listdir("."):
    print("A kovetkezo mappa feldolgozasa tortenik: " + name)
    tar.add(name)
tar.close()

csomagmerete = os.stat("/home/backup_archive/" + date_time + "/www.tar.gz").st_size / (1024 * 1024)
print("A csomagolas befejezodott, a csomag merete: " + str(round(csomagmerete, 2)) + " MB")

try:
    os.mkdir(adatb, 0o777)
except OSError:
    print("A mappa letrehozasa nem sikerult, a program kilep.")
    message = """Subject: """ + szervernev + """ - sikertelen backup
        
        A script nem tudott backupot kesziteni, mert a /home/backup_archive/""" \
              + date_time + """/adatbazisok mappa nem tudott letrejonni
        """

    with smtplib.SMTP_SSL("mailserver", 465, ssl.create_default_context()) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message)

    exit()
    shutil.rmtree('/home/backup_archive/' + date_time)
else:
    print("Sikerult a kovetkezo mappa letrehozasa: %s " % adatb)

for db in adatbazisok:
    lunda_dump = "mysqldump -h localhost -u" + db_username + " -p" + db_password + " " + db \
                 + "> " + "/home/backup_archive/" \
                 + date_time + "/adatbazisok/" + db + ".sql"
    print("A kovetkezo adatbazis kerul exportalasra: " + db)
    os.system(lunda_dump)

md5_hash = hashlib.md5()
with open("/home/backup_archive/" + date_time + "/www.tar.gz", "rb") as f:
    # Read and update hash in chunks of 4
    for byte_block in iter(lambda: f.read(4096), b""):
        md5_hash.update(byte_block)
    print("A csomag MD5 hash erteke: " + md5_hash.hexdigest())

print("FTP szerverre masolas kovetkezik..")

ftp = FTP()
ftp.connect(ftp_host, ftp_port)
ftp.login(ftp_username, ftp_password)


def placefiles(ftp_parancs, ftp_utvonal):
    for fajlnevek in os.listdir(ftp_utvonal):
        localpath = os.path.join(ftp_utvonal, fajlnevek)
        if os.path.isfile(localpath):
            # print("STOR", fajlnevek, localpath)
            ftp_parancs.storbinary('STOR ' + fajlnevek, open(localpath, 'rb'))
        elif os.path.isdir(localpath):
            # print("MKD", fajlnevek)
            try:
                ftp_parancs.mkd(fajlnevek)

            # ignore "directory already exists"
            except error_perm as e:
                if not e.args[0].startswith('550'):
                    raise
            # print("CWD", fajlnevek)
            ftp_parancs.cwd(fajlnevek)
            placefiles(ftp_parancs, localpath)
            # print("CWD", "..")
            ftp_parancs.cwd("..")


placefiles(ftp, ftp_path)
ftp.quit()

message = """Subject: {0} - sikeres backup\n\nA(z) {1} szerveren keszulo backup sikeresen befejezodott.\n
A csomag merete: {2} MB \nA kovetkezo adatbazisok kerultek lementesre (mappaba): {3}\nA backupok 
helye: {4} szerveren a(z) {5} felhasznalo home mappaja\nA letrejott fajlok torlesre kerultek helymegtakaritas 
celjabol a forras szerverrol.""".format(
    szervernev, szervernev, str(round(csomagmerete, 2)), ', '.join(adatbazisok), ftp_host, ftp_username)

shutil.rmtree('/home/backup_archive/' + date_time)

with smtplib.SMTP_SSL("mailserver", 465, ssl.create_default_context()) as server:
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, message)
    exit()
