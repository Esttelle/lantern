#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import subprocess
import sys
import time
from pprint import pprint


def parsearguments():
    parser = argparse.ArgumentParser(description='run cascade training')
    parser.add_argument('-pos', '--positivefilename', type=str, help='positive sample file',
                        default='/home/gongxijun/data/lantern/data/image/pos.txt')
    parser.add_argument('-neg', '--negativefilename', type=str, help='negative sample file',
                        default='/home/gongxijun/data/lantern/data/image/neg.txt')
    parser.add_argument('-m', '--maxfarate', help='max false alarm rate',
                        type=float, default=0.5)
    parser.add_argument('-d', '--dstdir', help='destination directory',
                        type=str, default='/home/gongxijun/data/lantern/data/model')
    parser.add_argument('-f', '--feature', help='feature type',
                        type=str, default='LBP')
    parser.add_argument('-w', '--width', help='width', type=int, default=90)
    parser.add_argument('-height', '--height', help='height', type=int, default=128)
    return parser.parse_args()


def createsamples(positivefile, vecdir='./vec', width=24, height=24):
    os.environ['PATH'] = '/bin:/usr/bin:/usr/local/bin'
    if not os.path.isdir(vecdir):
        os.mkdir(vecdir)
    numpos = len(open(positivefile).readlines())
    print('samples: %d' % (numpos,))
    vecfile = vecdir + '/' + positivefile.split('/')[-1] + '.vec'
    cmdline = ['opencv_createsamples', '-info', positivefile,
               '-vec', vecfile, '-num', str(numpos), '-w', str(width), '-h', str(height)]
    print(' '.join(cmdline))
    try:
        p = subprocess.Popen(cmdline, cwd='./', shell=False,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, close_fds=True)
    except OSError as e:
        print(e)
        sys.exit(-1)

    while True:
        line = p.stdout.readline()
        if not line:
            break
        print(line.rstrip())
    ret = p.wait()
    print('')

    return (vecfile, numpos)


def traincascade(dstdir, vecfile, numpos, negativefilename, featuretype='LBP', maxfarate=0.5,
                 width=24, height=24):
    if not os.path.isdir(dstdir):
        os.mkdir(dstdir)
    numpos = int(round(numpos * 0.85))
    numneg = len(open(negativefilename).readlines())
    cmdline = [
        'opencv_traincascade', '-data', dstdir,'-numStages',str(20), '-vec', vecfile,
        '-bg', negativefilename, '-numPos', str(numpos), '-numNeg', str(numneg),
        '-featureType', featuretype, '-maxFalseAlarmRate', str(maxfarate),
        '-w', str(width), '-h', str(height)
    ]
    print(' '.join(cmdline))

    try:
        print('Start cascade training')
        p = subprocess.Popen(cmdline, cwd='./', shell=False,
                             stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, close_fds=True)
    except OSError as e:
        print(e)
        sys.exit(-1)

    while True:
        line = p.stdout.readline()
        if not line:
            break
        print(line.rstrip())
    ret = p.wait()


if __name__ == '__main__':
    args = parsearguments()
    positivefilename = args.positivefilename
    negativefilename = args.negativefilename
    maxfarate = args.maxfarate
    dstdir = args.dstdir
    feature = args.feature
    width = args.width
    (vecfile, numpos) = createsamples(positivefilename, width=width, height=args.height)
    ts = time.time()
    traincascade(dstdir, vecfile, numpos, negativefilename, feature, maxfarate, width, args.height)
    processtime = int(time.time() - ts)
    print('process time: %s' % (str(processtime),))
