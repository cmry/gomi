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
\\large\\textbf{---ti---}
\\vspace*{0.5cm}
\\end{figure}
---tr---
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

bib = {}

inil = {'Van ': 'van ', 'Den ': 'den ', 'Der ': 'der ', 'De ': 'de ',
        'Het ': 'het ', "'T ": "'t ", 'Des ': 'des ', 'Op ': 'op '}
titl = ['and', 'the', 'a', 'for', 'in']

def sanitize(texs, istex=None):
    """
    Escapes any colliding characters with LaTeX, correct stupid unicode
    characters, and do a clean-up on some other user/system errors.

    :param texs: str abstract (or any) text in unicode
    :return: str sanitized text ready for LaTeX compiling
    """
            # names
    cust = {'Veronique':                                    u'V\u00E9ronique',
            'Ngoc Thi Do':                                  u'Do',
            'Antal van den Bosch':                          u'Antal van Den Bosch',
            # afils
            'Language and Translation Technology Team, ':   u'',
            # user errors
            'CLARIN for Linguists LOT ':                    u'CLARIN%20for%20Linguists%20LOT%20',
            '2014 Summerschool Illustration ':              u'2014%20Summerschool%20Illustration%20',
            '1 2014-06-22':                                 u'1%202014-06-22',
            'htttp':                                        u'http',
            # LaTeX collides
            '{':                                            u'\{',
            '}':                                            u'\}',
            " ''":                                          u" ``",
            " '":                                           u" `",
            "&":                                            u"\&",
            "~":                                            u"\~",
            "\%":                                           u"%",
            "%":                                            u"\%",  # wtf?
            "_":                                            u"\_",
            # crappy mac unicode stuff
            u'\u00A0':                                      u" ",
            u'\u00AD':                                      u"",
            # system errors
            "&amp;":                                        u"&",
            "amp;":                                         u''
            }
    
    for orig, repl in cust.iteritems():
        texs = texs.replace(orig, repl)
    if not istex:  # text only
        texs = texs.replace('\n', ' ')
        texs = token_url(texs, True)
    return texs


def token_url(text, fn=False):
    """
    Recognizes URLs in text and format them so that they will be
    placed in a footnote underneath the abstract. It also makes sure
    that certain stylistic clashes are omitted, for example a colon
     before the footnote number.

    :param text: str unicode text
    :return: str with footnoted URLs
    """
    # TODO: smarter handling of footnote
    urls = findall(' ?(?:(?:http|ftp|https):\/\/[a-z./0-9%]|\/?www).*(?:\.[a-z]{2,5}|\/)(?: |\n|\.|\)|,|$)', text)
    if urls:
        for u in urls:
            lm = u[len(u)-1:]  # try to trim stuff before the URL
            u = u[:-1] if (lm == '.' or lm == ')' or lm == ',') else u  # trim
            text = text.replace(u, ("\\footnote{" if fn else '') + " \\url{"+u+"}" + ("}" if fn else ''))  # insert footnote
    if fn:
        burls = findall('(?:,|\.)' + ('\\\\footnote\{' if fn else '') + ' \\\\url\{.*\}' + ('\}' if fn else ''), text)
        if burls:  # if , or . before footnote, switch them
            for bu in burls:
                text = text.replace(bu, bu[1:]+bu[0])
    return text


def format_ref(refs, label):
    """
    Given a string with references able to be splitted by newline,
    adds to global bib a tuple with a unique id, and the label it
    will use to refer to the page it's mentioned on, as well as a
    cleaned out version of the references. Custom part had to be
    implemented because one of the references was split up by
    newlines within references.

    :param refs: str unicode text snippet with \n splittable refs
    :param label: here sec:title is used to pageref to the abstract
    :return: None (adds to global bib)
    """
    global bib
    refs = refs.split('\n')
    # TODO: find a way to handle the custom line better
    refs = list(' '.join(refs)) if 'Ramage' in ' '.join(refs) else refs  # custom!
    for n in refs:
        if len(n) > 10:
            n = n[1:] if n.startswith(' ') else n
            n = token_url(n)
            bib[(hash(n), label)] = n


def format_text(text, title):
    """
    Finds the boundary between the list of references and the
    abstract text, will provide a label for the abstract, and
    pipe the found references towards format_ref function.

    :param text: the abstracts text, including refs
    :param title: the title of the abstract
    :return: str unicode with the abstract text and label, no refs
    """
    ref = findall(r'\n(?:[Rr]eference)|(?:REFERENCE)[sS]?[:]?', text)
    brf = findall(r'\n\[[0-9]\]', text)
    label = 'tit:' + str(hash(title))
    if brf or ref:
        tl = text.split((brf[-1:] if (brf and not ref) else ref[-1:])[0])
        text, ref = tl[0], sanitize(tl[1], True)
        format_ref(ref, label)
    return sanitize(text)+'\n'+'\\label{'+label+'}'


def format_toc(tit, name_l):
    """
    Accepts title and list of tuples with names from the authors
    of the abstract, and will convert these into a formatted unicode
    LaTeX toc entry.

    :param tit: str unicode abstract title (no linebreaks)
    :param name_l: list str with authors
    :return: str unicode ToC entry for the abstract
    """
    # TODO: refactor this function to look more like the one on fazzeh.github.io
    aut = ', '.join([('\\newline ' if (name_l.index(n) == 4 and len(', '.join([n[0]+' '+n[1] for n in name_l[:3]]))
                                       < 72) else '') + n[0]+' '+n[1] for n in name_l])
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
    Checks if there is a character in the title which has priority
    as being a split marker.

    :param tl: str unicode title of the abstract
    :return: int index of the priority if exists, else None
    """
    mark = [':' if ':' in i else False or '(' if '(' in i else False for i in tl]
    if '(' in mark:
        if mark.index('(') > 2:
            return mark.index('(')
    elif ':' in mark:
        if mark.index(':') > 2:
            return mark.index(':')+1


def format_title(tit):
    """

    :param tit:
    :return:
    """
    global titl
    tit = sanitize(tit)
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
    st_name = name[0]+' '+name[1]
    return st_name + " \\index{" + name[1] + ", " + name[0] + "} "


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


def get_refs():
    global bib
    bib = OrderedDict(sorted(bib.items(), key=lambda (k, v): v))
    bibt = '\\chapter*{Bibliography} \n\\begin{itemize} \n'
    for tup, cit in bib.iteritems():
        bibt += '\\item[\\pageref{'+tup[1]+'}] '+cit+'\n'
    bibt += '\n \\end{itemize}'
    return bibt


def main():

    tree = ET.parse('abstracts.xml')
    submissions = tree.getroot()
    abst = {}

    for submission in submissions:
        if not 'REJECT' in submission[3].text:
            dc = str(tex)

            sd = submission.attrib['id']
            kw = [k.text for k in submission[1]]

            title = format_title(submission[0].text)
            dc = dc.replace('---ti---', title)
            dc = dc.replace('---te---', format_text(submission[2].text, title))

            names = [(sanitize(entry[0].text), lower_dut(entry[1].text)) for entry in submission[4]]
            afils = [sanitize(entry[3].text) for entry in submission[4]]
            mails = [(sanitize(entry[2].text) if entry[2].text else '') for entry in submission[4]]

            dc = dc.replace('---tr---', format_toc(title, names))
            dc = dc.replace('---na---', format_table(names, afils, mails))
            abst[submission[0].text] = dc

    with open('./tex/bos_test.tex', 'r') as i:
        o = open('./tex/bos_o.tex', 'w')
        i = i.read()
        i = i.replace('% abstracts', '\n'.join([v for v in OrderedDict(sorted(abst.items(),
                          key=lambda t: t[0])).itervalues()]).encode("utf-8"))
        i = i.replace('% refl', get_refs().encode("utf-8"))
        o.write(i)
        o.close()

if __name__ == '__main__':
    main()