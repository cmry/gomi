__author__ = 'chris'

from query import *
import urllib2

def urban(message):

    q = Query()
    query = q.search(message)

    def_nr = 0

    if " " in query:
        query = query.replace(" ","%20")
    try:
        def_nr = int(query[len(query)-1])-1
        query = query[:-4]
    except:
        pass

    url = 'http://www.urbandictionary.com/define.php?term=' + query

    usock = urllib2.urlopen(url)
    data = usock.read()
    usock.close()
    def_raw = ""
    def_list = []
    concat = False
    record = True
    divcount = 0

    for line in data.split():
        if divcount == 2:
            definition = ""
            def_raw = def_raw.replace('<div class="example">','\n\n')
            def_raw = def_raw.replace(' class="definition"','')
            for character in def_raw:
                if character == "<":
                    record = False
                    continue
                elif character == ">":
                    record = True
                    continue
                elif record == False:
                    continue
                else:
                    definition += character

            definition = definition.replace("&#39;","'")
            definition = definition.replace("&quot;",'"')
            def_list.append(definition)
            divcount = 0
            concat = False
            def_raw = ""
        elif line.startswith('class="definition"') or concat == True:
            def_raw += (" "+line)
            concat = True
            if "</div>" in line:
                divcount += 1
        else:
            continue

    if def_list:
        return q.cut(def_list[def_nr])
    else:
        return "Corrupted cores! We're in luck."