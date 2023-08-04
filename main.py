# -*-coding:utf8;-*-
from bs4 import BeautifulSoup
import requests
import util
from anybinding import Bind
import db
import os


user = os.environ.get('DOCKERHUB_USER')
password = os.environ.get('DOCKERHUB_PASSWORD')
docker = Bind("docker", direct_output=True)
container_image = "phpid/xampp"
docker.login("-u", user, "-p", password)
# scrape xampp
html_doc = requests.get("https://www.apachefriends.org/download.html").text
soup = BeautifulSoup(html_doc, 'html.parser')
linux_html = soup.select('li#download-linux')[0]
datas = util.parse_data(linux_html)
# update version in database
for data in datas:
    version, release, tag = util.parse_version(data["version"])
    if not db.version_exists(version):
        db.add_version(version)

latest = db.get_latest_version()
# build
update = False
for data in datas:
    version, release, tag = util.parse_version(data["version"])
    if db.need_update(release):
        print(f"building xampp {release}..")
        file = f"php{version}.Dockerfile"
        util.write(file, util.dockerfile.replace(
            "{{download_uri}}", data["download"]))
        if version == latest:
            docker.build("--pull", "-t", container_image+": latest",
                         "-t", container_image+":"+tag, "-f", file, ".")
            docker.push(container_image+":"+tag)
            docker.push(container_image)
        else:
            docker.build("--pull", "-t", container_image +
                         ":"+tag, "-f", file, ".")
            docker.push(container_image+":"+tag)
        update = True
        db.update_release(version, release)
    else:
        print(f"no need update for xampp {release}!")

if update:
    db.close()
