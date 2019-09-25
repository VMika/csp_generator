# CSP-Generator 

## Build status

[![pipeline status](https://scm.int.excellium.lu/pentest-team/csp_generator/badges/master/pipeline.svg)](https://scm.int.excellium.lu/pentest-team/csp_generator/commits/master)

## Goal
This project is designed to generate Content Securiy Policies (CSP) for a webpage based on crawled content and analysis of requests made by the original URL. By compiling all calls to external ressources and crawling static content, the tool aims to generate an accurate and secure CSP without breaking integrity of the resource (keeping all functionnalities up and the apparence of the website).

## Resources
* Firefox documentation on CSP - [https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
* Google CSP checker - [https://csp-evaluator.withgoogle.com/](https://csp-evaluator.withgoogle.com/)
* W3 standard for CSP v2 [https://www.w3.org/TR/CSP2/](https://www.w3.org/TR/CSP2/)
 
## Overview
The projet relies on scraping content from a URL and then following every links to retrieve all the accessible content for a given domain. It makes use of Selenium in order to render dynamic content and getting an accurate list of the site resources.

Then it sorts all the content into corresponding directive, build a CSP for the domain and generate a report that hightlights the parts that could be changed in order to get a more restrictive, hence secure, CSP.

The goal of the tool is to generate a CSP that will be manually reviewed and ready tu use as-is but designed to be enhanced over time.

### Technical architecture
Steps of the execution :
1. The user submits a start_url and an allowed_domain to the web interface
2. The crawler query the URL and extracts all the links found recursively until all links are visited/no more links are available. It returns an URL list and is stored in the SQLite database
3. The CSP Generator loop through URLs and for each URL, query the content and renders it with Selenium and send it to sorters
4. Sorters are fed the content by the generator and extracts relevant sources to append to the CSP and return data to the generator. It also returns the flags that correspond to the findings that will be displayed in the report. Outputs are stored in the databse.
5. CSP Generator builds the final CSP header and send flags to the Report Generator to build necessary data to view the report.
6. Results are available for consultation through the web interface

![](report/images/workflow.png)

## Installations for Unix systems

This installation procedure is based on my personal experience when installing the projet on a Docker container designed to build tests. The base docker image was Alpine Linux (light image designed to have as little packages as possible) so this installation procedure should work fairly well for most of the Unix distribution. I did the following installation procedure an a pristine Ubuntu Virtual Machine and it worked without any problems.

### Requirements
* Python 3.7 installed (3.6 should work but has not been tested)
* Firefox (version >57)
* Git
* A working version of Java


### Installation procedure
1. Clone the repository
```bash
git clone https://github.com/VMika/csp_generator.git
```
2. Instal venv and create a virtual environment into the directory you just created (if you don't want to use venv, just go to step 4 but keep in mind your already installed packages might create conflicts).
```bash
apt-get install python3-venv
python -m venv ./venv
```
3. Activate the virtual envrionment
```bash
source venv/bin/activate
```
4. Install required packages. Depending on your distribution you may already have some installed.
```bash
apt-get install libffi-dev
apt-get install python3-dev
apt-get install libxslt-dev
apt-get install python3-lxml
```

5. Install the wheel tool to build the projet
```bash
pip install wheel
```

6. If you are on a distribution that doesn't handle graphical rendering (for example Alpine Linux) you will need to install a virtual graphical handler that allows headless browser. You should not need that.
```bash
apt-get install xvfb
apt-get install firefox #or firefox-esr
Xvfb :99 -ac &
export DISPLAY=:99
```

7. Install all the dependancies
```bash
pip install -r requirements.txt
```

8. Get the server running from the root of the project
```bash
python flask_twisted/app/flask_twisted.py
```

9. The server is now up on localhost:9000 !

## On Windows system

### Requirements
* Python 3.7 installed (3.6 should work but has not been tested)
* Firefox (version >57)
* Git
* A working version of Java
* Microsoft Visual C++ 14.0
* SQLite3

### Installation procedure

The installation on Windows should be pretty seamless as the OS takes care of external packages for you. As long as you have all the pre-requisites and have not installed other versions of the used packages, it should not raise any issue. Once again I tested this installation on a Virtual Machine.

1. Clone the repository
```bash
git clone https://github.com/VMika/csp_generator.git
```

2. Instal venv and create a virtual environment into the directory you just created (if you don't want to use venv, just go to step 5 but keep in mind your already installed packages might create conflicts).
```bash
apt-get install python3-venv
python -m venv ./venv
```

3. Activate the virtual envrionment
```bash
.\venv\Scripts\activate
```
4. Install `win32api` module
```bash
pip install pypiwin32
```

5. Install requirements
``` bash
pip install -r requirements.txt
```

#### Possible errors
During this step you might get the following errors : 
* Incremental fail import 
```bash
 raise DistutilsError(msg)
    distutils.errors.DistutilsError: Could not find suitable distribution for Requirement.parse('incremental>=16.10.1')
```
Fix : Upgrade the incremental package
```bash
pip install --upgrade incremental
 ```

* Microsoft Visual C++ is required enventhough it is installed
```bash
error: Microsoft Visual C++ 14.0 is required. Get it with "Microsoft Visual C++ Build Tools": https://visualstudio.microsoft.com/downloads/

``` 
Fix : Upgrade the `setuptools` package
```bash
pip install -uupgrade setuptools
```

#### Installation of Microsoft Visual C++
If you're struggling with Microsoft Visual C++ installation and still get the error related to it on the installation process, follow this procedure :

1. Go to https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019
2. Scroll down to the section "Tools for Visual Studio 2019"
3. Download the binary "Build tools for Visual Studio 2019"
4. The installer will prompt you with a menu allowing you to choose which module you want to install
5. Choose the Visual Studio Build Tools
6. Let the installation run
