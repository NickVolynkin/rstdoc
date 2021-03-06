#!/usr/bin/env python
# encoding: utf-8 

#def gen_head(lns,**kw):
#    b,e = list(rindices('^"""',lns))[:2]
#    return lns[b+1:e]
#def gen_head(lns,**kw)
#def gen_api(lns,**kw):
#    yield from doc_parts(lns,signature='py',prefix='reflow.')
#def gen_api

"""
.. _`rstreflow`:

rstreflow
=========

rstreflow: shell command
reflow: rstdoc module

Reflow tables and paragraphs in a rst document produced from a docx.

Post-process a docx in this order::

    rstfromdocx doc.docx
    rstlisttable doc/doc.rst > doc/tmp.rst
    rstuntable doc/tmp.rst > doc/tmp1.rst
    rstreflow doc/tmp1.rst > doc/tmp2.rst
    rstreimg doc/tmp2.rst > doc/tmp3.rst
    rm doc/doc.rst
    mv doc/tmp3.rst doc/doc.rst
    rm doc/tmp*

Check the intermediate results.

Else one can also do inplace::

    rstfromdocx doc.docx
    rstlisttable -i doc/doc.rst
    rstuntable -i doc/doc.rst
    rstreflow -i doc/doc.rst
    rstreimg -i doc/doc.rst

.. note:: DOCX to RST using Pandoc

   ``rstfromdocx -lurg doc.rst`` converts a docx to RST and
   does all the post-processing in one step.

   It is adviced, though, to compare the output with the original and do some manual
   corrections here and there.

"""


#''' starts api doc parts (see doc_parts())
'''
API
---

.. code-block::

   import rstdoc.reflow as reflow

'''


import re
from textwrap import wrap
from .listtable import gridtable, row_to_listtable
from .retable import retable, titlerex, re_title

_pgrphrex=[
        re.compile(r'\s+'),
        re.compile(r'\s*-(\s|$)'),
        re.compile(r'\s*\*(\s|$)'),
        re.compile(r'\s*\* -(\s|$)'),
        re.compile(r'\s*\w\.(\s|$)'),
        re.compile(r'\s*#\.(\s|$)'),
        re.compile(r'\s*:?\w\+:(\s|$)'),
        ]

def reflowparagraph(
      p #paragraph
      ,sentence=False #if True lines are split at the end of the sentence
      ):
    '''
    Reflow a paragaph using ``textwarp.wrap``. Possibly split sentences.
    '''
    if p:
        if len(p)==3 and titlerex.match(p[0]) and titlerex.match(p[2]) or len(p)==2 and titlerex.match(p[1]):
            re_title(p,0,0)
            yield from p
        elif p[0][0] == '=': #simple table
            yield from p
        elif len(p[0])>3 and p[0][0:3]=='.. ': #directive, comment
            yield from p
        else:
            st = 0
            mo = ''
            for rp in _pgrphrex:
                m = rp.match(p[0])
                if m:
                    if m.span()[1] > st:
                        st = m.span()[1]
                        mo = m.group(0)
            if p[0] and st < len(p[0]) and p[0][st] in '|+':
                yield from p
            else:
                if sentence:
                    txt = ' '.join([p[0][st:]]+[pp.strip() for pp in p[1:]])
                    wraptxt = []
                    for ph in txt.split('. '):
                        wraptxt.extend(wrap(ph))
                        wraptxt[-1]+='.'
                    else:
                        wraptxt[-1]=wraptxt[-1][:-1]
                else:
                    txt = '\n'.join([p[0][st:]]+[pp.strip() for pp in p[1:]])
                    wraptxt = wrap(txt)
                lmo = 0
                if not wraptxt:
                    yield mo
                else:
                    for tl in wraptxt:
                        if not lmo:
                            yield mo+tl
                            lmo = len(mo)
                        else:
                            yield ' '*lmo+tl
        del p[:]

def reflowparagraphs(
      lns #lines from rst file
      ,sentence=False #if True lines are split at the end of the sentence
      ):
    '''
    Reflow paragraphs using |reflow.reflowparagraph|.
    '''
    #yield from lns
    p = []
    literal = False
    reflowp = lambda p: reflowparagraph(p,sentence)
    re_literal = re.compile('^(?!\.\. ).*::\s*$')
    for dd in lns:
        if dd.strip() == '':
            dds = ['']
        else:
            dds = dd.splitlines()
        for d in dds:
            if literal and d and d[0]!=' ':
                p.append(d)
                literal = False
            elif literal:
                yield d
            elif re_literal.search(d):
                p.append(d)
                yield from reflowp(p)
                literal = True
            else:
                dstrip = d.strip()
                if not dstrip:
                    yield from reflowp(p)
                    yield d
                elif any([rp.match(dstrip) for rp in _pgrphrex]):
                    yield from reflowp(p)
                    p.append(d)
                else:
                    p.append(d)
    yield from reflowp(p)

def rmextrablankline(
      lns #lines from rst file
      ):
    '''
    Remove excessive blank lines.
    '''
    bc = 0
    for d in lns:
        if not d.strip():
            bc = bc+1
        else:
            bc = 0
        if bc < 3:
            yield d

def no3star(
      lns #lines from rst file
      ):
    '''
    Removes three stars, as they are not supported by docutils.
    '''
    for d in lns:
        #d='***Hello***'
        res = d.replace('***','**')
        #d='**space before **'
        res = re.sub('(\w)\s+\*\*\s*$',r'\1**',d)
        #d='**'
        res = re.sub('^\s*\*\*\s*$',r'',d)
        yield res

def noblankend(
      lns #lines from rst file
      ):
    '''
    Removes blanks at the end of the line.
    '''
    nbe = re.compile('\s+$')
    for d in lns:
        yield nbe.sub('',d)

class reflowrow():
    '''
    This replaces |listtable.row_to_listtable| in |listtable.gridtable| to reflow a grid table.
    '''
    def __init__(self):
        self.tbl = []
    def __call__(self,row,colwidths,withheader,join,indent,tableend):
        for lne in row_to_listtable(row,colwidths,withheader,join,indent,tableend):
            if not tableend or lne.strip():
                self.tbl.append(lne)
        if tableend:
            yield from retable(self.tbl)
            del self.tbl[:]

def reflow(
      lns #lines from rst file
      ,join='1' #0 no space, 1 with space, 2 keep as-is
      ,sentence=False #if True lines are split at the end of the sentence
      ):
    '''
    Combines all rst corrections of this file.
    '''
    r = reflowrow()
    for ln in noblankend(
            no3star(
                rmextrablankline(
                    reflowparagraphs(
                        gridtable(lns, join, r),
                        sentence
                        )
                    )
                )
            ):
        yield ln+'\n'

def main(
        **args #keyword arguments. If empty the arguments are taken from ``sys.argv``.
        ):
    '''
    This corresponds to the |rstreflow| shell command.
    '''
    import codecs
    import sys
    import argparse

    if not args:
        parser = argparse.ArgumentParser(
            description='''Reflow paragraphs and tables, for the latter using join as for listtable''')
        parser.add_argument('INPUT', type=argparse.FileType('r',encoding='utf-8'), nargs='+', help='RST file(s)')
        parser.add_argument('-j', '--join', action='store', default='012',
                help='''e.g.002. Join method per column: 0="".join; 1=" ".join; 2="\\n".join''')
        parser.add_argument('-s', '--sentence', action='store_true', default=False,
                help='''Break lines at the end of sentences.''')
        parser.add_argument('-i', '--in-place', action='store_true', default=False,
                help='''change the file itself''')
        args = parser.parse_args().__dict__

    for infile in args['INPUT']:
        lns = infile.readlines()
        infile.close()
        if args['in_place']:
            f = open(infile.name,'w',encoding='utf-8',newline='\n')
        else:
            #'≥'.encode('cp1252') # UnicodeEncodeError on Windows, therefore...  makes problems with pdb, though
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
            sys.stdin = codecs.getreader("utf-8")(sys.stdin.detach())
            f = sys.stdout
        try:
            f.writelines(reflow(lns,args['join']))
        finally:
            if args['in_place']:
                f.close()


if __name__ == '__main__':
    main()

