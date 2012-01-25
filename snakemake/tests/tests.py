import sys
import os
from os.path import join
from subprocess import call
from tempfile import mkdtemp
import hashlib
#from snakemake import snakemake # TODO use this instead of calling the executable

__author__ = "Tobias Marschall, Marcel Martin"


def dpath(path):
	"""get path to a data file (relative to the directory this
	test lives in)"""
	return join(os.path.dirname(__file__), path)


# TODO import snakemake instead
EXECUTABLE = dpath('../bin/snakemake')


def md5sum(filename):
	data = open(filename, 'rb').read()
	return hashlib.md5(data).hexdigest()


def run(path, **params):
	"""
	Test the Snakefile in path.
	There must be a Snakefile in the path and a subdirectory named
	expected-results.
	"""
	results_dir = join(path, 'expected-results')
	snakefile = join(path, 'Snakefile')
	assert os.path.exists(snakefile)
	assert os.path.exists(results_dir) and os.path.isdir(results_dir), \
		'{} does not exist'.format(results_dir)
	tmpdir = mkdtemp()
	try:
		call('cp `find {} -maxdepth 1 -type f` {}'.format(path, tmpdir), shell=True)
		additional_params = params['target'] if 'target' in params else ''
		exitcode = call('{0} -d {1} -s {1}/Snakefile {2} > /dev/null 2>&1'.format(EXECUTABLE, tmpdir, additional_params), shell=True)

		# TODO
		# The snakemake call changes the current working directory, so
		# we need to remember it and restore it below.

		# TODO use this instead of call() above
		#olddir = os.getcwd()
		#exitcode = snakemake(snakefile, directory=tmpdir, **params)
		#os.chdir(olddir)
		assert exitcode == 0, "exit code is not zero, but {}".format(exitcode)
		for resultfile in os.listdir(results_dir):
			if not os.path.isfile(resultfile):
				continue # skip .svn dirs etc.
			targetfile = join(tmpdir, resultfile)
			expectedfile = join(results_dir, resultfile)
			assert os.path.exists(targetfile), 'expected file "{}" not produced'.format(resultfile)
			assert md5sum(targetfile) == md5sum(expectedfile), 'wrong result produced for file "{}"'.format(resultfile)
	finally:
		call(['rm', '-rf', tmpdir])


def test01():
	run(dpath("test01"))


def test02():
	run(dpath("test02"))


def test03():
	run(dpath("test03"), target='test.out')


def test04():
	run(dpath("test04"), target='test.out')


# alternativ zum obigen (dann wird das in der Ausgabe von
# nosetests allerdings nicht als einzelner Test angezeigt)
#def tests():
	#for f in os.listdir(dpath('.')):
		#path = dpath(f)
		#print('f:', f, os.path.dirname(__file__))
		#print("path:", path)
		#if not os.path.isdir(path):
			#continue
		#if not f.startswith('test'):
			#continue
		#if not os.path.exists(join(path, 'Snakefile')):
			#print('Warning: {}/Snakefile does not exist, skipping directory'.format(path), file=sys.stderr)
			#continue
		#run(path)

