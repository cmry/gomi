#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'chris'
__version__ = '12.14'

import xml.etree.ElementTree as ET
from collections import OrderedDict
from copy import deepcopy
from re import findall

tex = '''
\\newpage

\\begin{figure}[t!]
\\centering
---tr---
\\large\\textbf{---ti---}
\\vspace*{0.5cm}
\\end{figure}
---na---
\\noindent
---te--- '''

btab = '''
\\begin{table}[t!]
\\makebox[\\textwidth]{
\\centering
\\begin{tabular}{---al---}
---ta--- '''

ctab = '''        
\\end{tabular} }
\\end{table} '''

inil = {'Van ': 'van ', 'Den ': 'den ', 'Der ': 'der ', 'De ': 'de ',
        'Het ': 'het ', "'T ": "'t ", 'Des ': 'des ', 'Op ': 'op '}
titl = ['and', 'the', 'a', 'for', 'in']

cust = {'Veronique Hoste':                  u"Hoste, V\u00E9ronique",
        'Quynh Ngoc Thi Do':                u'Do, Quynh',
        'Antal van den Bosch':              u'van Den Bosch, Antal',
        'Antal van Den Bosch':              u'van Den Bosch, Antal'}


def sanitize(texs):
    """
    This function is used to escape any colliding characters with
    LaTeX, correct stupid unicode characters, and do a clean-up on
    some other user/system errors.
    :param texs: str abstract (or any) text in unicode
    :return: str sanitized text ready for LaTeX compiling
    """
    # LaTeX collides
    texs = texs.replace(" ''", " ``")
    texs = texs.replace(" '", " `")
    texs = texs.replace("&", "\&")
    texs = texs.replace("~", "\~")
    texs = texs.replace("\%", "%")
    texs = texs.replace("%", "\%")
    texs = texs.replace("_", "\_")
    texs = texs.replace("}", "\}")
    texs = texs.replace("{", "\{")
    # crappy unicode stuff
    texs = texs.replace(u'\u00A0', " ")  # screw you mac
    texs = texs.replace(u'\u00AD', "")   # and some more
    texs = texs.replace('\n', ' ')
    # user errors
    texs = texs.replace('htttp', 'http')
    # system errors
    texs = texs.replace("&amp;", "&")
    texs = texs.replace("amp;", '')
    texs = token_url(texs)
    return texs


def token_url(text):
    """
    This function is used to recognize URLs in text and format them
    so that they will be placed in a footnote underneath the abstract.
    It also makes sure that certain stylistic clashes are omitted, for
    example a colon before the footnote number.
    :param text: str unicode text
    :return: str with footnoted URLs
    """
    urls = findall(' ?(?:http|ftp|https):\/\/[a-z./0-9%].*(?:\.[a-z]{2,5}|\/)(?: |\n|\.|\)|,|$)', text)
    if urls:
        for u in urls:
            lm = u[len(u)-1:]  # try to trim stuff before the URL
            u = u[:-1] if (lm == '.' or lm == ')' or lm == ',') else u  # trim
            text = text.replace(u, "\\footnote{\\url{"+u+"}}")  # insert footnote
    burls = findall('(?:,|\.)\\\\footnote\{\\\\url\{.*\}\}', text)
    if burls:  # if , or . before footnote, switch them
        for bu in burls:
            text = text.replace(bu, bu[1:]+bu[0])
    return text


def check_double_ref(text):
    textx = text.replace("],", "] ,")
    textx = textx.replace("])", "] )")
    textix = textx.lower().split()
    textii = deepcopy(textix)
    textii.remove('[1]')
    return textii


def format_text(text):
    texti, upto = text.split(), False
    # if '[1]' in text:
    #     textii = check_double_ref(text)
    #     if '[1]' in textii:
    #         upto = textii.index('[1]')
    # if 'references:' in texti:
    #     upto = texti.index('references:')
    # if '\nreference' in text.lower():
    #     if 'references' in texti:
    #         upto = texti.index('references')
    #     if 'references:' in texti:
    #         upto = texti.index('references:')
    #     if 'reference:' in texti:
    #         upto = texti.index('reference:')
    ref = findall(r'\n[Rr]eference[s]?[:]?', text)
    brf = findall(r'\[0-9\]', text)
    if brf and not ref:
        print "TARD ALERT: "+tex
    else:
        # want to cutoff, avoid split because it craps up the newlines
        refl = texti[texti.index(ref[-1:])]
        refi = refl.pop(0)


    # if upto:
    #     tex, i = [], 0
    #     for x in text.split():
    #         if i >= upto:
    #             break
    #         else:
    #             tex.append(x)
    #             i += 1
    #     text = ' '.join(tex)
    # check page 44, 48

    # refnr = findall(r'\[[0-9]\]', ' '.join(textl[0]))
    # if len(textl) > 1:
    #     refs = textl[1].split('\n')
    #     exit(refs)
    return text


def format_toc(tit, name_l):
    aut = ', '.join([('\\newline ' if (name_l.index(n) == 4 and len(', '.join(name_l[:4])) < 72) else '') + n[0]+' '+n[1] for n in name_l])
    aut = aut.split(' \\newline')
    tit = sanitize(tit.replace('\\\\ ', ''))
    tit = "\\addcontentsline{toc}{section}{\\emph{" + tit + "}} \n" + \
          "\\addtocontents{toc}{\\protect\\vspace{0.2em}} \n" + \
          "\\addtocontents{toc}{" + aut[0] + " \\hfill" + ("\\newline" if len(aut) > 1 else '') + "} \n"
    if len(aut) > 1:
        tit += "\\addtocontents{toc}{\\hspace*{1.2em}" + aut[1] + "} \n"
    tit += "\\addtocontents{toc}{\\protect\\vspace{1em}} \n"
    return tit


def check_prio(tl):
    """

    :param tl:
    :return:
    """
    mark = [':' if ':' in i else False or '(' if '(' in i else False for i in tl]
    if '(' in mark:
        if mark.index('(') > 2:
            return mark.index('(')
    elif ':' in mark:
        if mark.index(':') > 2:
            return mark.index(':')+1


def format_title(tit):
    global titl
    if 62 < len(tit) < 96:
        tl = tit.split()
        tl.insert(len(tl)/2 if not check_prio(tl) else check_prio(tl), '\\\\')
        for word in list(set(tl) & set(titl)):
            if tl.index(word)-tl.index('\\\\') == 1 and ':' not in tl[tl.index(word)-2]: # page 41
                a, b = tl.index(word), tl.index('\\\\')
                tl[a], tl[b] = tl[b], tl[a] 
        tit = ' '.join(tl)
    if tit[-1:] == '.':
        tit = tit[:-1]
    return tit


def lower_dut(surename):
    global inil
    for ini in inil.iterkeys():
        if ini in surename:
            surename = surename.replace(ini, inil[ini])
    return surename


def format_name(name):
    global cust
    st_name = name[0]+' '+name[1]
    if st_name not in cust:
        return st_name + " \\index{" + name[1] + ", " + name[0] + "} "
    else:
        return st_name + " \\index{" + cust[st_name] + "} "


def format_table(namel, afil, maill):
    global ctab, btab
    ltab = []
    while len(namel) > 0:
        ntab = deepcopy(btab)
        if len(namel) == 1:
            if len(ltab) != 0:
                ntab = ctab + ntab
            ntab += ctab
            name_e = format_name(namel.pop(0))
            ta = "%s \\\\ {%s} \\\\ {\\texttt{%s}} \\\\" % (name_e, afil.pop(0), maill.pop(0))
            al = 'c'
        else:
            name_e1 = format_name(namel.pop(0))
            name_e2 = format_name(namel.pop(0))
            ta = "%s & %s \\\\ {%s} & {%s} \\\\ {\\texttt{%s}} & {\\texttt{%s}} \\\\" % \
                 (name_e1, name_e2, afil.pop(0), afil.pop(0), maill.pop(0), maill.pop(0))
            al = 'cc'
        if al == 'cc' and len(ltab) >= 1:
            ntab = " & \\\\ \n "+ta
        else:
            ntab = ntab.replace('---ta---', ta)
            ntab = ntab.replace('---al---', al)
        ltab.append(ntab)
    if '\\end{table}' not in ltab[len(ltab)-1]:
        ltab.append(ctab)
    return '\n'.join(ltab)


tree = ET.parse('abstracts.xml')
submissions = tree.getroot()
abst = {}

for submission in submissions:
    if not 'REJECT' in submission[3].text:
        dc = str(tex)

        sd = submission.attrib['id']
        kw = [k.text for k in submission[1]]

        titl = format_title(submission[0].text)
        dc = dc.replace('---ti---', titl)
        dc = dc.replace('---te---', sanitize(format_text(submission[2].text)))

        names = [(sanitize(entry[0].text), lower_dut(entry[1].text)) for entry in submission[4]]
        afils = [sanitize(entry[3].text) for entry in submission[4]]
        mails = [(sanitize(entry[2].text) if entry[2].text else '') for entry in submission[4]]

        dc = dc.replace('---tr---', format_toc(titl, names))
        dc = dc.replace('---na---', format_table(names, afils, mails))
        abst[submission[0].text] = dc

with open('./tex/bos_test.tex', 'r') as i:
    o = open('./tex/bos_o.tex', 'w')
    i = i.read()
    o.write(i.replace('% abstracts', '\n'.join([v for v in OrderedDict(sorted(abst.items(),
                      key=lambda t: t[0])).itervalues()]).encode("utf-8")))
    o.close()