#-*-coding:utf8;-*-
from bs4 import BeautifulSoup
import re


dockerfile = """
FROM ubuntu:latest
MAINTAINER Am K<amek_chesster@yahoo.com.hk>

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update --fix-missing > /dev/null
# Set root password to root, format is 'user:password'.
RUN echo 'root:root' | chpasswd
# install dependency
RUN apt-get -yqq install net-tools crudini curl git zip unzip wget > /dev/null

# git config
RUN git config --global user.email "amek_chesster@yahoo.com.hk" && git config --global user.name "Am K"

# download xampp
RUN wget {{download_uri}} -O xampp-linux-installer.run --no-check-certificate
RUN chmod +x xampp-linux-installer.run
RUN bash -c './xampp-linux-installer.run' > /dev/null
RUN rm ./xampp-linux-installer.run
RUN ln -sf /opt/lampp/lampp /usr/bin/lampp

# Enable XAMPP web interface(remove security checks)
RUN sed -i.bak s'/Require local/Require all granted/g' /opt/lampp/etc/extra/httpd-xampp.conf

# Enable includes of several configuration files
RUN mkdir /opt/lampp/apache2/conf.d && \
    echo "IncludeOptional /opt/lampp/apache2/conf.d/*.conf" >> /opt/lampp/etc/httpd.conf

# path xampp assignment
ENV PATH="/opt/lampp/bin:${PATH}"

# Enable php eror
RUN crudini --set /opt/lampp/etc/php.ini PHP display_errors On 
# Install Composer
RUN curl -sS https://getcomposer.org/installer | php -- \
        --install-dir=/opt/lampp/bin \
        --filename=composer
# path .composer assignment
ENV PATH="~/.composer/vendor/bin:${PATH}"

# Install NVM - NODE
ENV NVM_VERSION v0.39.3
ENV NODE_VERSION 18.15.0
ENV NVM_DIR /usr/local/nvm
RUN mkdir $NVM_DIR
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash

ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH
RUN echo "source $NVM_DIR/nvm.sh && \
    nvm install $NODE_VERSION && \
    nvm alias default $NODE_VERSION && \
    nvm use default" | bash

RUN apt-get clean

ENV XAMPP_ROOT /opt/lampp/htdocs/
VOLUME [ "/var/log/mysql/", "/var/log/apache2/", "/opt/lampp/htdocs/" ]

# MySQL
EXPOSE 3306
# web
EXPOSE 80
# ftp
EXPOSE 21
WORKDIR /opt/lampp/htdocs/
CMD ["lampp", "start"]
"""
dockerfile = dockerfile.strip()

def remove_html_tags(text):
	clean = re.compile('<.*?>')
	return re.sub(clean, '', text)

def normalize_key(k):
	if k.strip() == "":
		return "download"
	return k.lower().strip()

def normalize_value(k, v):
	if k.lower() == "checksum":
		ret = {}
		r = re.findall('title=\"(.*)\"', str(v))
		ret["md5"] = r[0]
		ret["sha1"] = r[1]
		return ret
	elif k.strip() == "":
		r = v.find("a",{"class":"button"}).get("href")
		return r+"?from_af=true"
	else:
		return remove_html_tags(str(v)).strip()

def parse_data(html):
	out = []
	html = f"<html>{html}</html>"
	soup = BeautifulSoup(html, 'html.parser')
	table = soup.find('table')
	headers = [header.text for header in table.find_all('th')]
	results = [{headers[i]: cell for i, cell in enumerate(row.find_all('td'))} for row in table.find_all('tr')]
	for array in results:
		res = {}
		for k, v in array.items():
			res[normalize_key(k)] = normalize_value(k, v)
		out.append(res)
	return list(filter(None, out))

def parse_version(version):
	release = version.split("/")[0].strip()
	v = release.split(".")
	tag = v[0]+"."+v[1]
	version = int(v[0]+v[1])
	return version, release, tag.strip()

def write(file, data):
	with open(file, "w") as f:
		f.write(data)
