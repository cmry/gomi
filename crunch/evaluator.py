__author__ = 'chris'

from core.util import *
from crunch.grapher import Grapher
import csv
import numpy as np
from glob import glob
from numpy import mean
from re import findall
from sklearn.metrics import classification_report

# normalizeren comments (gem per dag) -> normaliseren artikelen per dag


class Evaluator:

    def __init__(self, func, fdir, mod, k):
        self.k_list = [1, 2, 3, 5]
        self.res = []

        Conv().graph_convergence([fdir+'_'+str(i)+'_fold'+'_'+mod for i in range(k)])
        exit()
        if func == 'tt':
            self.__eval_proc([fdir+'_ti_'+mod])
        if func == 'kf':
            self.__eval_proc([fdir+'_'+str(i)+'_fold'+'_'+mod for i in range(k)])

    def __eval_proc(self, dirl):
        self.res.append("\n \n Results: \n")
        self.res.append("--- MAP @ k ---")
        Mapk(self, dirl)
        self.res.append("--- MAP @ k filtered ---")
        Mapk(self, dirl, 'filter')
        self.res.append("--- Regular metrics ---")
        Metrics(self, dirl)
        for r in self.res:
            print r

    @staticmethod
    def get_label_index(res_dir):
        li = list()
        with open(res_dir+'/01000/label-index.txt', 'r') as f:
            for i in f.readlines():
                li.append(i.strip('\n'))
        return li

    @staticmethod
    def get_actual_labels(res_dir):
        ref = glob(res_dir+'/*distributions-res.csv')[0].split('-')[0].split('/')
        ref = ref[len(ref)-1]+'.csv'
        with open(res_dir+'/../'+ref) as f:
            cf = csv.reader(f, delimiter=',', quotechar='"')
            for line in cf:
                yield line[5].split()

    @staticmethod
    def get_predicted_labels(res_dir, li):
        for i in gen_csv(glob(res_dir+'/*distributions-res.csv')[0]):
            sort_d = {}
            for j in range(1, len(i)):
                sort_d[li[j-1]] = float(i[j]) if float(i[j]) <= 1.0 else 0.0
            yield list(sortd(sort_d, 'v', True))


class Mapk():

    def __init__(self, ev, dirl, f=None):
        kd = {k: 0 for k in ev.k_list}
        for res_dir in dirl:
            for k in ev.k_list:
                list_index = ev.get_label_index(res_dir)
                actual = ev.get_actual_labels(res_dir)
                predicted = ev.get_predicted_labels(res_dir, list_index)
                kd[k] += self.__mapk(actual, predicted, k, f)
        for k, v in sortd(kd, 'k', False).iteritems():
            ev.res.append('map('+str(k)+'): \t '+str(v/len(dirl)))
        ev.res.append('\n\n')

    def __mapk(self, actual, predicted, k=10, f=None):
        l = []
        for a, p in zip(actual, predicted):
            if not f:
                l.append(self.apk(a, p, k))
            else:
                reltop = ['Privacy', 'NSA', 'PRISM', 'Edward_Snowden', 'Prism', 'prism', 'privacy']
                if any(i in reltop for i in a):
                    l.append(self.apk(a, p, k))
        return np.mean([l])

    @staticmethod
    def apk(actual, predicted, k=1):
        score, num_hits, predicted = 0.0, 0.0, predicted[:k] if len(predicted) > k else predicted
        for i, p in enumerate(predicted):
            if p in actual and p not in predicted[:i]:
                num_hits += 1.0
                score += num_hits / (i+1.0)
        return score / min(len(actual), k)


class Metrics:

    def __init__(self, ev, dirl):
        md = {k: '' for k in ev.k_list}
        for k in ev.k_list:
            y_true, y_pred = [], []
            for res_dir in dirl:
                list_index = ev.get_label_index(res_dir)
                actual = ev.get_actual_labels(res_dir)
                predicted = ev.get_predicted_labels(res_dir, list_index)
                ct, cp = self.clask(actual, predicted, k)
                y_true += ct
                y_pred += cp
            target_names = ['non-priv', 'priv']
            md[k] = classification_report(y_true, y_pred, target_names=target_names)
        for k, v in sortd(md, 'k', False).iteritems():
            ev.res.append('Metrics at '+str(k)+': \n '+v)

    def clask(self, actual, predicted, k=1):
        y_true, y_pred = [], []
        for a, p in zip(actual, predicted):
            reltop = ['Privacy', 'NSA', 'PRISM', 'Edward_Snowden', 'Prism', 'prism', 'privacy'] # expand
            y_pred.append(self.binary_clas(reltop, p, k))
            y_true.append(1 if any(i in reltop for i in a) else 0)
        return y_true, y_pred

    def binary_clas(self, rt, predicted, k):
        return 1 if any(i in rt for i in predicted[:k]) else 0


class Conv:

    def __init__(self):
        pass

    @staticmethod
    def graph_convergence(res_dir):
        res_dir = res_dir[0]
        out_name = res_dir.split('/')
        out_name = out_name[len(out_name)-1]
        line_name = out_name.split('_')[0]
        dr, x, y = glob(res_dir+'/0*'), [], []
        for i in dr:
            y.append(int(findall('[0-9]{5}', i)[0]))
            with open(i+'/summary.txt', 'r') as f:
                t_x = []
                for line in f.readlines():
                    if not line.startswith('\t') and findall('[A-Z]', line):
                        t_x.append(float(line.split()[1]))
                x.append(mean(t_x))
        Grapher.convergence_plot(out_name, line_name, x, y)