#!/usr/bin/env python

import sys, subprocess, os, multiprocessing
from distutils.spawn import find_executable

execdir = os.path.dirname(os.path.realpath(__file__))
julia = find_executable('julia')
if not julia:
    for d in ['/home/skwarkmj/sw/julia/bin', '.', '~/julia']:
        if os.path.exists(d + '/julia'):
            julia = d + '/julia'
if not julia:
    sys.stderr.write('Cannot find Julia!\n')
    sys.exit(0)


print "Using: ",julia

alignment = sys.argv[1]

if len(sys.argv) > 2:
    cpus = int(sys.argv[2])
else:
    cpus = min(8,multiprocessing.cpu_count())

print "Using %d cpus." % cpus

if not os.path.exists(alignment):
    sys.stderr.write('Error: Input alignment {:s} does not exist.\n'.format(alignment))
    sys.exit(0)

stem = alignment[:alignment.rfind('.')]

if os.path.exists(stem + '.gdca'):
    sys.stderr.write("Error: Output file exists.\n")
    sys.exit(0)

a = subprocess.check_output('{0:s} -p {1:d} {2:s}/rungDCA.jl {3:s} {4:s}.gdca'.format(julia, cpus, execdir, alignment, stem), shell=True)

f = open(stem + '.gneff', 'w')
f.write(a)
f.close()
