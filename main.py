#! /usr/bin/python3.4
import os
import sys
import webbrowser
from datetime import datetime
import re
import xml.etree.cElementTree as eTree


# coding: Windows-1252

# -----------------------------------Configuration Constants------------------------------------ #

versionVisualStudio = 10  # two last digit of Visual Studio Version
for arg in sys.argv:
    print(arg)
    if arg == os.path.basename(__file__):
        print("Welcome To Autobuild Project")
    elif arg == "10" or arg == "12" or arg == "15":
        versionVisualStudio = arg
        break
    else:
        print("")
        exit(0)
# ----------------------------------------Functions--------------------------------------------- #


# Generate HTML Header
def index_header(html, location="style.css"):
    html.write("""<!DOCTYPE html>
    <html>
        <head>
            <meta charset=utf-8 />
            <title>Liste des builds</title>
            <link rel="stylesheet" href=""" + location + """ />
        </head>
        <body>""")


# Generate HTML Footer
def index_footer(html):
    html.write("<footer>" + "Date & Time of the last Update : " + str(datetime.now()) + "</footer></body></html>")


# Get error quantity
def filter_nb(log, index):
    if index == -1:  # Prevent crash if output is corrupted
        nb = "Error"
    else:
        if log[index-4].isdigit():
            nb = "+99"
        else:
            if log[index-3].isdigit():
                nb = int(log[index-3])*10
            else:
                nb = 0
            nb += int(log[index-2])
    return nb


def filter_time(log, index):
    if index == -1:
        nb = "Error"
    else:
        nb = log[index:index+11]
    return nb


def check_error_cmake(log):
    if log.find("Generating done") == -1:
        return "NOT OK"
    else:
        return "OK"


# Parse compilation errors
def check_error_compil(log):
    # Filthy function to return number of errors or warnings can't recover more than 99 error's
    if osType == "Windows":
        index = log.find("Warning(s)")
        warnings = filter_nb(log, index)

        index = log.find("Error(s)")
        errors = filter_nb(log, index)

        index = log.find("Time Elapsed ")
        time = filter_time(log, index+13)

    else:  # Clang,gcc tested
        errors = 0
        warnings = 0
        time = "Unknown"
        if log == "[100%] Built target main\n":
            print("Nothing has been updated")
        else:
            n = re.findall("(\w+.cpp|\w+.cc|\w+.c):\d+:\d+: warning: .*", log)
            warnings = len(n)
            n = re.findall("(\w+.cpp|\w+.cc|\w+.c):\d+:\d+: error: .*", log)
            errors = len(n)
            print("nb_errors", errors, "nb_warnings", warnings)
    return errors, warnings, time


# Generate HTML CMake Output
def parsing_result_cmake(html, log):
    html.write("<h3>CMake log : </h3><p>")
    if log == "":
        'There is a problem, might be with the Compiler Version,' \
            'see constant at the start of the script : "versionVisualStudio"'
    else:
        for letter in log:
            if letter == '\n':
                html.write("<br />")
            else:
                html_config.write(letter)
    html.write("</p>")


# Generate HTMl Comilation Output
def parsing_result_compil(html, log, nbWarningError):
    if osType == "Windows":
        index = log.find("Build succeeded.") + 16
        if index == 15:  # 15 = -1+16 because res.find() returns -1 if not found
            index = log.find("Build FAILED.") + 13
            if index == 12:  # Same here
                result = "Error with the build, there is the raw output : \n"+log
            else :
                result = log[index:log.__sizeof__()]
        else:
            result = log[index:log.__sizeof__()]

        html.write("<h3>Compilation log : </h3>")
        index = result.find("(ClCompile target) -> ")+22
        html.write("<table border='1'><tr><th colspan='3'>Erreur(s) et Warning(s)</th></tr>"
                   "<tr><td>Fichier : Ligne</td><td>Code Erreur</td><td>Descriptif</td></tr>")
        m = re.findall("(\w+.cpp|\w+.cc|[\w*.?\w*]+)\((\d+,?\d*)\)", log[index:log.__sizeof__()])
        n = re.findall(": (error) (\w+)?: (.*?.vcxproj])|: (warning) (\w+)?: (.*?.vcxproj])" +
                       "|LINK : (fatal error) (\w+): (\w+.+.vcxproj])?",
                       log[index:log.__sizeof__()])
        print("Number of Warning(s) and/or Error(s)" + str(nbWarningError))
        for i in range(0, nbWarningError):
            if n[i][0] == "error":
                html.write("<tr><td>" + m[i][0] + " : " + m[i][1] + "</td><td class = 'red'>" + n[i][1] + "</td><td>" +
                           n[i][2] + "</td></tr>")
            if n[i][3] == "warning":
                html.write("<tr><td>" + m[i][0] + " : " + m[i][1] + "</td><td class = 'orange'>" + n[i][4] + "</td><td>" +
                           n[i][5] + "</td></tr>")
            if n[i][6] == "fatal error":
                html.write("<tr><td>" + "Fatal Error" + "</td><td class = 'red'>" + n[i][7] + "</td><td>" +
                           n[i][8] + "</td></tr>")

    else:
        html.write("<h3>Compilation log : </h3>")
        html.write("<table border='1'><tr><th colspan='3'>Erreur(s) et Warning(s)</th></tr>"
                   "<tr><td>Fichier</td><td>Ligne</td><td>Descriptif</td></tr>")
        n = re.findall("(\w+.cpp|\w+.cc|\w+.c):(\d+):\d+: (error|warning): (.*)", log)
        print("Number of Warning(s) and/or Error(s)" + str(nbWarningError))
        for i in range(0, nbWarningError):
            if n[i][2] == "error":
                html.write("<tr><td>" + n[i][0] + "</td><td class = 'red'>" + n[i][1] + "</td><td>" +
                           n[i][3] + "</td></tr>")
            if n[i][2] == "warning":
                html.write("<tr><td>" + n[i][0] + "</td><td class = 'orange'>" + n[i][1] + "</td><td>" +
                           n[i][3] + "</td></tr>")


# ------------------------------------Looking for Platform type-------------------------------- #
if os.name == "nt":
    osType = "Windows"
    if versionVisualStudio == "10":
        compiler = """ "Visual Studio 10" """
    elif versionVisualStudio == "12":
        compiler = """ "Visual Studio 12 2013 Win64" """
    elif versionVisualStudio == "15":
        compiler = """ "Visual Studio 14 2015 Win64" """
    cmake = "cmake -G " + compiler
    compilation = "cmake --build . --target ALL_BUILD"  # Debug or Release
    if versionVisualStudio == 10:
        os.system(""" "C:/Program Files (x86)/Microsoft Visual Studio 10.0/VC/bin/vcvars32.bat" """)
    elif versionVisualStudio == 12:
        os.system(""" "C:/Program Files (x86)/Microsoft Visual Studio 12.0/VC/bin/vcvars32.bat" """)
    elif versionVisualStudio == 15:
        os.system(""" "C:/Program Files (x86)/Microsoft Visual Studio 14.0/VC/bin/vcvars32.bat" """)
    errorRedirect = ""
    print("Windows Platform")
elif os.name == "posix":
    osType = "Unix"
    compiler = """ "Unix Makefiles" """
    cmake = "cmake -G " + compiler
    compilation = "cmake --build ."
    sys.stderr = sys.stdout
    errorRedirect = "2>&1"
    print("Unix Platform")
else:
    print("Platform not Supported")
    exit(0)

# ------------------------------------Main---------------------------------------- #

# Connection to Perforce
# os.system("p4 login")
# Synchronisation of P4
# os.system("p4 sync")


# Opening and Parsing XML file
log = open("res.log", "w")
tree = eTree.parse("config.xml")
root = tree.getroot()
print(len(root), "project(s) have been found")

# Opening HTML file
html_main = open("index.html", "w")
index_header(html_main)

for build in root:
    nb_project = 1  # debug
    name = build.attrib["name"]
    location = build.attrib["location"]
    cmakelistLocation = build.attrib["cmakelists"]
    html_main.write("<table><tr><th colspan='6'>" + name + "</th></tr>" +
                    "<tr><td rowspan='2'>Name</td><td colspan='2' rowspan='2'>CMake</td>" +
                    "<td colspan='2'>Build</td><td rowspan='2'>Time</td></tr>" +
                    "<tr><td>Errors</td><td>Warnings</td></tr>")
    baselocation = str(os.getcwd())
    information_project = ""
    for configuration in build:
        configurationName = configuration.attrib["name"]
        argument = configuration.attrib["argument"]
        try:
            os.chdir(location)
            os.chdir(baselocation)
        except OSError:
            print("Dossier du projet érroné, vérifier l'xml de configuration ou l'arborescence")
            information_project += "Dossier du projet errone, verifier l'xml de configuration ou l'arborescence</br>"
            continue  # Folder not found, pass on all this config
        try:
            os.chdir(location+"build")
            os.chdir(baselocation)
        except OSError:
            os.mkdir(location+"build")
            print("Created dir build")

        html_config = open(location + "build/" + configurationName + ".html", "w")
        index_header(html_config, baselocation + "/style.css")
        print("project : ", name)  # debug

        # Changing directory & Creating if necessary
        try:
            os.chdir(location+"build/"+osType)
        except OSError:
            os.mkdir(location+"build/"+osType)
            os.chdir(location+"build/"+osType)
            print("Created dir", osType)

        try:
            os.chdir(configurationName)
        except OSError:
            os.mkdir(configurationName)
            os.chdir(configurationName)
            print("Created dir", configurationName)

        # CMake ( and build )

        p = os.popen(cmake + " " + argument + " " + baselocation + "/" + location + cmakelistLocation + " " +
                     errorRedirect)
        res = p.read()
        cmake_error = check_error_cmake(res)
        log.write(res)
        print(res)
        parsing_result_cmake(html_config, res)
        check_error_cmake(res)
        print(configurationName)
        p = os.popen(compilation+" --config " + configurationName + " " + errorRedirect)
        res = p.read()
        log.write(res)
        nb_errors, nb_warnings, time = check_error_compil(res)
        if nb_errors == "Error" or nb_warnings == "Error":
            html_main.write("<tr><td><a href='" + location + "build/" + configurationName + ".html'>" +
                            configurationName + "</a></td><td colspan='2'" + "class ='" +
                            ('green' if cmake_error == "OK" else 'red') + "'>" + cmake_error + "</td><td class=red>" +
                            str(nb_errors) + "</td><td class=orange>" + str(nb_warnings) + "</td><td>" + time +
                            "</td></tr>")
            information_project += ("Error with the Cmake (or the script) check XML path or CmakeList.txt for config : "
                                    + configurationName + "</br>")
        else:
            parsing_result_compil(html_config, res, nb_errors + nb_warnings)  # print only output of compilation
            html_main.write("<tr><td><a href='" + location + "build/" + configurationName + ".html'>" +
                            configurationName + "</a></td><td colspan='2'" + "class ='" +
                            ('green' if cmake_error == "OK" else 'red') + "'>" + cmake_error +
                            "</td><td class='" + ('green' if nb_errors == 0 else 'red') + "'>" + str(nb_errors) +
                            "</td><td class='" + ('green' if nb_warnings == 0 else 'orange') + "'>" + str(nb_warnings) +
                            "</td><td>" + time + "</td></tr>")
        index_footer(html_config)
        os.chdir(baselocation)
        nb_project += 1
    html_main.write("</table>" + information_project + "</br>")

index_footer(html_main)
webbrowser.open('index.html')
