#!/usr/bin/env python3
# This code was developed with the assistance of ChatGPT-4o (OpenAI)

import os
import sys
import time
import random
import warnings
import argparse
import numpy as np
import h5py
import _predict_parallel

# fraction of trees to use (prediction time scales linearly with the number of trees,
# while expected precision is roughly the same for values > 0.3
treedepth = 100
treefraction = 0.3

parser = argparse.ArgumentParser()
parser.add_argument('GaussDCA')
parser.add_argument('plmDCA')
parser.add_argument('MLContactPrediction')
parser.add_argument('NetsurfRSA')
parser.add_argument('SSfile')
parser.add_argument('AlignmentStats')
parser.add_argument('Alignment')
parser.add_argument('ForestLocations')
parser.add_argument('MaxDepth', type=int)
parser.add_argument('Outfile')
parser.add_argument('NumberThreads', type=int, nargs='?', default=1)
args = parser.parse_args()

maxdepth = args.MaxDepth

num_threads = args.NumberThreads

if int(maxdepth) <= 0:
    forestlocation = args.ForestLocations + '/tlayer{:d}'
else:
    forestlocation = args.ForestLocations + '/tlayer{:d}-' + str(maxdepth)

for i in range(5):
    if not os.path.exists(forestlocation.format(i) + '.hdf5'.format(i)):
        raise IOError('Forest data for layer {:d} is missing.\n'.format(i))

firststart = time.time()


def parsePSIPRED(f):
    SSdict = {}
    try:
        x = open(f).read().split('\n')
    except:
        return SSdict
    for l in x:
        y = l.split()
        if len(y) != 6:
            continue
        i = int(y[0])
        SSdict[i] = [float(y[3]), float(y[4]), float(y[5])]
    return SSdict


def parseNetSurfP(f):
    netSurfdict = {}
    for l in open(f).readlines():
        al = []
        x = l.split()
        if l.find('#') == 0:
            continue
        if l[0] not in ['B', 'E']:
            y = ['E']
            y.extend(x)
            x = y
        for y in [4, 6, 7, 8, 9]:
            al.append(float(x[y]))
        netSurfdict[int(x[3])] = al
    return netSurfdict


def parsePSSM(alignment):
    import numpy as np  # Required if not already imported globally

    pssm = {}
    one2number = 'ARNDCEQGHILKMFPSTWYV-'
    
    # Background frequencies (without gaps)
    bi = [0.0825, 0.0553, 0.0406, 0.0545, 0.0137, 0.0393, 0.0675, 0.0707, 0.0227,
          0.0595, 0.0966, 0.0584, 0.0242, 0.0386, 0.0470, 0.0657, 0.0534, 0.0108,
          0.0292, 0.0687]
    
    # Initialize background frequency dictionary (excluding gap)
    b = {aa: bi[i] for i, aa in enumerate(one2number[:-1])}

    freqs = {}        # Counts per position per amino acid
    seqcount = 0      # Total number of sequences
    gapcount = 0      # Number of gap characters
    coverage = []     # Sequence coverage at each position

    # Read alignment file
    for l in open(alignment):
        if l.startswith('>'):
            continue  # Skip FASTA headers
        x = l.strip()
        if len(x) < 3:
            continue  # Skip too-short sequences

        seqcount += 1
        coverage.append((len(x) - x.count('-')) / float(len(x)))

        for i, aa in enumerate(x):
            freqs.setdefault(i, {})
            freqs[i][aa] = freqs[i].get(aa, 0) + 1
            if aa == '-':
                gapcount += 1

    if seqcount == 0 or len(freqs) == 0:
        raise ValueError("No valid sequences found in alignment file.")

    # Estimate background frequency for gaps
    b['-'] = gapcount / (seqcount * len(freqs)) if seqcount > 0 else 1e-6

    entropy = []

    for i in sorted(freqs.keys()):
        q = []
        for aa in one2number:
            b_aa = b.get(aa, 1e-6)
            denom = b_aa * seqcount
            if denom == 0:
                denom = 1e-6  # prevent division by zero
            f = freqs[i].get(aa, 0) / denom
            if f > 0:
                logf = np.log(f)
                q.append(logf)
                q.append(f * logf)
                entropy.append(f * logf)
            else:
                q.append(np.log(0.1 / denom))
                q.append(0)
                entropy.append(0)
        pssm[i + 1] = q



    # Return PSSM, mean entropy, and coverage statistics
    return pssm, np.mean(entropy), [
        np.min(coverage), np.max(coverage),
        np.mean(coverage), np.median(coverage)
    ]


def parseStats(f):
    stats = []
    ff = open(f).readlines()
    if len(ff) != 6:
        warnings.warn(RuntimeWarning(f + ' has incorrect format!'))
        return [-1, -1, -1, -1, -1, -1]
    for l in ff:
        stats.append(float(l.split()[-1]))
    return stats


def parseContacts(f):
    contacts = set()
    for l in open(f):
        x = l.split()
        if len(x) != 3:
            raise IOError('Incorrect format for ' + f)
        if float(x[-1]) < 8:
            contacts.add( (int(x[0]), int(x[1])))
    return contacts

contacts = {}
maxres = -1
outfile = args.Outfile
sys.stderr.write('Doing ' + outfile + '\n')
accessibility = parseNetSurfP(args.NetsurfRSA)
SSdict = parsePSIPRED(args.SSfile)
stats = parseStats(args.AlignmentStats)
pssm = parsePSSM(args.Alignment)
entropy = pssm[1]
coverage = pssm[2]
pssm = pssm[0]

selected = set()
cmap_preds = (args.GaussDCA, args.plmDCA, args.MLContactPrediction)
for index in range(3):
    contacts[index] = {}
    d = cmap_preds[index]
    r = []
    if not os.path.exists(d):
        warnings.warn(RuntimeWarning(d + ' does not exist!'))
        continue
    infile = open(d).readlines()
    for m in infile:
        if d.find('gdca') > -1:
            x = m.split()
            c = 2
        elif d.find('plm') > -1:
            x = m.split(',')
            if len(x) != 3:
                raise IOError(d + ' has wrong format!')
        else:
            x = m.split()
            if len(x) < 3 or x[2] != '0' or x[3] != '8':
                continue
            c = -1
        if len(x) < 3:
            continue
        aa1 = int(x[0])
        aa2 = int(x[1])
        if aa1 > maxres:
            maxres = aa1
        if aa2 > maxres:
            maxres = aa2    
        if x[c].find('nan') > -1:
            score = -3
        else:
            score = float(x[c])
        contacts[index][(aa1, aa2)] = score
        contacts[index][(aa2, aa1)] = score
        if not aa2 > aa1:
            continue
        selected.add((aa1, aa2))

clist = []
for c in contacts[0].keys():
    q = [c]
    for i in contacts.keys():
        try:
            q.append(contacts[i][c])
        except:
            q.append(-3)
    clist.append(q)

selected2 = set()
for i in contacts.keys():
    clist.sort(key=lambda x: -x[i+1])
    counter = -1
    c = 0
    while counter < maxres:
        j = clist[c]
        selected2.add(j[0])
        c += 1
        if abs(j[0][0] - j[0][1]) > 4:
            counter += 1

maxscores = []
meantop = []
stdtop = []
for index in range(3):
    if contacts[index]:
        maxscores.append(max(contacts[index].values()))
    else:
        maxscores.append(0.0)
    q = []
    for s in list(selected2):
        try:
            q.append(contacts[index][s])
        except:
            pass
    meantop.append(np.mean(q))
    stdtop.append(np.std(q))

selected = list(selected)
selected.sort()
lastseeny = -1

X = []
Y = []
sys.stderr.write('Reading in data\n')
sys.stderr.flush()
count = 0
allcount = len(selected)
start = time.time()

for s in selected:
    count += 1
    q = [abs(s[0]-s[1])]

    for ss in stats:
        q.append(ss)
    q.append(entropy)
    q.extend(coverage)
        
    q.append(maxscores[0])
    q.append(maxscores[1])
    q.append(maxscores[2])

    for i in range(-5, 6):
        for j in range(-5, 6):
            for index in range(3):
                try:
                    q.append(contacts[index][(s[0]+i, s[1]+j)])
                    q.append((contacts[index][(s[0]+i, s[1]+j)] - meantop[index])/stdtop[index])
                except:
                    q.append(0)
                    q.append(0)

        for i in range(-4, 5):
                try:
                        q.extend(SSdict[s[0]+i])
                except:
                        q.extend((0, 0, 0))

        for i in range(-4, 5):
                try:
                        q.extend(SSdict[s[1]+i])
                except:
                        q.extend((0, 0, 0))
    
    for i in range(-4, 5):
        try:
            q.extend(accessibility[s[0] + i])
        except:
            q.extend((0, 0, 0, 0, 0))
    
    for i in range(-4, 5):
        try:
            q.extend(accessibility[s[1]+i])
        except:
            q.extend((0, 0, 0, 0, 0))

    q.extend(pssm[s[0]])
    q.extend(pssm[s[1]])
    
    X.append(q)

sys.stderr.write('\n')
sys.stderr.flush()


def predict(dir, X_pred):
    if not os.path.exists(dir + '.hdf5'):
        raise IOError('Directory {:s} does not contain proper random forest!\n'.format(dir))

    predictions = np.zeros(len(X_pred))
    X_pred = np.asarray(X_pred)

    trunks = []
    compares = []
    leafs = []

    with h5py.File(dir + '.hdf5', "r") as h5f:
        trees = list(h5f.keys())  # convert KeysView to list for shuffling and slicing
        random.shuffle(trees)
        trees = trees[:int(len(trees) * treefraction)]

        for t in trees:
            trunks.append(h5f[t + '/trunks'][()])
            compares.append(h5f[t + '/compares'][()])
            leafs.append(h5f[t + '/leafs'][()])

    shape = (len(trunks), max(t.shape[0] for t in trunks), max(t.shape[1] for t in trunks))
    trunks_ = np.full(shape, np.nan, dtype=np.int64)

    for i, t in enumerate(trunks):
        trunks_[i, :t.shape[0], :t.shape[1]] = t

    leafs_ = np.full((len(leafs), max(l.shape[0] for l in leafs)), np.nan, dtype=np.float64)

    for i, t in enumerate(leafs):
        leafs_[i, :t.shape[0]] = t

    compares_ = np.full((len(compares), max(c.shape[0] for c in compares)), np.nan, dtype=np.float64)
    for i, t in enumerate(compares):
        compares_[i, :t.shape[0]] = t
    del leafs, trunks, compares

    _predict_parallel.predict(trunks_, leafs_, compares_, X_pred, predictions, num_threads=num_threads)
    print(predictions)
    return predictions

# first layer
sys.stderr.write('\nPredicting base layer:\n')
p = predict(forestlocation.format(0), X)
previouslayer = {}

with open(outfile + '.l0', 'w') as of:
    for t in range(len(p)):
        of.write('{:d} {:d} {:7.5f}\n'.format(selected[t][0], selected[t][1], p[t]))
        try:
            previouslayer[selected[t][0]][selected[t][1]] = p[t]
        except:
            previouslayer[selected[t][0]] = {}
            previouslayer[selected[t][0]][selected[t][1]] = p[t]


Xp = X
Yp = selected
for layer in range(1, 6):
    X = []
    sys.stderr.write('\nPredicting convolution layer {:d}:\n'.format(layer))
    for p in range(len(Xp)):
        y = Yp[p]
        q = list(Xp[p])
        for i in range(-5, 6):
            for j in range(-5, 6):
                try:
                    q.append(previouslayer[y[0] + i][y[1] + j])
                except:
                    q.append(-3)
        X.append(q)

    p = predict(forestlocation.format(layer), X)

    previouslayer = {}
    with open(outfile + '.l{:d}'.format(layer), 'w') as of:
        for t in range(len(p)):
            of.write('{:d} {:d} {:7.5f}\n'.format(Yp[t][0], Yp[t][1], p[t]))
            try:
                previouslayer[Yp[t][0]][Yp[t][1]] = p[t]
            except:
                previouslayer[Yp[t][0]] = {}
                previouslayer[Yp[t][0]][Yp[t][1]] = p[t]

sys.stderr.write('\n\nSuccesfully completed in {:7.1f} seconds\n'.format(time.time() - firststart))
