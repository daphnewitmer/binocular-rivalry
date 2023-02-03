import glob
import sys
import os
import pickle as pkl
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
from scipy import stats


def main():
    subj_idx = sys.argv[1]
    run = sys.argv[2]

    data_dir = os.path.abspath('data')
    template = os.path.join(data_dir, '{subj_idx}_{run}_*_outputDict.pkl'.format(**locals()))

    target = sorted(glob.glob(template))[-1]

    print("Using the following filename:\n{}".format(target))

    df = get_behavior_onsets(target)
    
    ipis = df[(df.key != 'mixed') & (~df.duration.isnull())].duration
    ipis_mixed = df[(df.key == 'mixed') & (~df.duration.isnull())].duration

    # Fit distribution
    ipis_pars = fit_distribution_ks(ipis, sp.stats.invgauss)
    ipis_mixed_pars = fit_distribution_ks(ipis_mixed, sp.stats.invgauss)

    # Plot fit for full percepts
    t = np.linspace(0, np.percentile(ipis, 99), 100)

    plt.hist(ipis.values, bins=20, normed=True)
    plt.plot(t, 
             sp.stats.invgauss(*ipis_pars.x).pdf(t), 
             label='Kolmogorov-Smirnov')
    plt.plot(t, 
             sp.stats.invgauss(*sp.stats.invgauss.fit(ipis)).pdf(t), 
             label='Maximum Likelihood')
    plt.title('Full percept distribution fit')
    plt.legend()

    ipis_fn = os.path.abspath(os.path.join('data', '{subj_idx}_{run}_ipi_full_pars.pdf'.format(**locals())))
    plt.savefig(ipis_fn)

    plt.figure()

    t = np.linspace(0, np.percentile(ipis_mixed, 99), 100)
    plt.hist(ipis_mixed.values, bins=20, normed=True)
    plt.plot(t, 
             sp.stats.invgauss(*ipis_mixed_pars.x).pdf(t), 
             label='Kolmogorov-Smirnov')
    plt.plot(t, 
             sp.stats.invgauss(*sp.stats.invgauss.fit(ipis_mixed)).pdf(t), 
             label='Maximum Likelihood')
    plt.title('Mixed percept distribution fit')
    plt.legend()

    ipis_mixed_fn = os.path.abspath(os.path.join('data', '{subj_idx}_{run}_ipi_mixed_pars.pdf'.format(**locals())))
    plt.savefig(ipis_mixed_fn)

    ipis_fn = os.path.abspath(os.path.join('data', '{subj_idx}_{run}_ipi_full_pars.txt'.format(**locals())))
    np.savetxt(ipis_fn, ipis_pars.x[np.newaxis, :], delimiter=', ')
    print("Saving parameters for full percept durations to {}".format(ipis_fn))

    ipis_mixed_fn = os.path.abspath(os.path.join('data', '{subj_idx}_{run}_ipi_mixed_pars.txt'.format(**locals())))
    np.savetxt(ipis_mixed_fn, ipis_mixed_pars.x[np.newaxis, :], delimiter=', ')
    print("Saving parameters for full percept durations to {}".format(ipis_mixed_fn))

def get_behavior_onsets(fn):
    
    with open(fn, 'rb') as f:
        _ = pkl.load(f)
        
    pars = pd.DataFrame(_['parameterArray'])
    df_ = _['eventArray']

    reg1 = re.compile('trial (?P<trial>[0-9]+) started at (?P<onset>[0-9]+\.[0-9]+)')
    reg2 = re.compile('trial (?P<trial>[0-9]+) phase (?P<phase>[0-9]+) started at (?P<onset>[0-9]+\.[0-9]+)')
    reg3 = re.compile('trial (?P<trial>[0-9]+) event (?P<key>[0-9]+) at (?P<onset>[0-9]+\.[0-9]+)')

    df = []

    phase = 0

    for trial_idx, trial in enumerate(df_):
        for event in trial:
            event = str(event)
            for i, r in enumerate([reg1, reg2, reg3]):
                if reg2.match(event):
                    phase = reg2.match(event).groupdict()['phase']
                if r.match(event):
                    row = r.match(event).groupdict()
                    row['type'] = i
                    row['trial'] = trial_idx
                    row['phase'] = phase
                    df.append(row)

    df = pd.DataFrame(df)
    df['type'] = df['type'].map({0:'Trial start', 1:'phase start', 2:'key press'})
    df['key'] = df['key'].map({'2':'red', '1':'mixed', '4':'green'})
    df['onset'] = df['onset'].astype(float)
    
#     df.loc[df.type == 'phase start', 'key'] = df.apply(lambda row: 'start phase %s' % row.phase, 1)
    keys = df[np.in1d(df.type, ['key press', 'phase start'])]#[['onset', 'key', 'trial']]
    
    keys = keys[(keys.phase == '2') & (keys.type == 'key press')]

    keys['onset'] = keys.onset - df[df.type == 'phase start'].iloc[0].onset
    
    keys['report'] = keys.trial.map(pars.report).astype(bool)
    
    keys['superfluous_button_press'] = keys.groupby('trial').key.apply(lambda d: d == d.shift(1))
    
    keys = keys[~keys.superfluous_button_press]
    keys = keys[keys.report]

    keys['duration'] = (keys['onset'] - keys.groupby(['trial']).onset.shift(1)).shift(-1)
    
    return keys

def fit_distribution_ks(values, dist, init_pars=None):
    
    if init_pars is None:
        init_pars = dist.fit(values)
    
    def cost_function(pars):
        return sp.stats.kstest(values, dist(*pars).cdf)[0]
        
    return sp.optimize.minimize(cost_function, [init_pars], options={'disp':True})

if __name__ == '__main__':
    main()
