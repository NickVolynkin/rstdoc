from waflib import Logs
Logs.colors_lst['BLUE']='\x1b[01;36m'
top='.'
out='../build'
def options(opt):
  opt.load('dcx',tooldir='rstdoc')
  opt.add_option("--tests", default=False, help="Run the tests") 
def configure(cfg):
  cfg.load('dcx',tooldir='rstdoc')
def build(bld):
  #defines bld.stpl(), bld.gen_files(), bld.gen_links(), bld.build_docs()
  bld.load('dcx',tooldir='rstdoc')
  if bld.options.tests:
      bld.exec_command('py.test --cov rstdoc --cov-report term-missing > doc/_testcoverage.rst')
  bld.recurse('doc')
