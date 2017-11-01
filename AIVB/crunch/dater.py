from crunch.evaluator import Evaluator
import csv
import datetime
from glob import glob
from collections import Counter


class Dater:

    def __init__(self, func, fdir, mod, k):
        #nu.nl
        src, prd, top, wek = ['tweakers.net'], ['ESP', 'OSP', 'ISP'], ['oft', 'ont'], [str(x) for x in range(1, 23)]
        self.res = {'_'.join([s[:1]+'-'+p+'-'+w+'-'+t, t, s, p]): [0, 0] for w in wek for t in top for s in src for p in prd}

        self.oft_art, self.ont_art, self.res_dir = [], [], []
        self.reltop = ['Privacy', 'NSA', 'PRISM', 'Edward_Snowden', 'Prism', 'prism', 'privacy']

        self.relab = {'2013-01': 'ESP', '2013-06': 'ISP', '2013-11': 'OSP',
                      '2013-02': 'ESP', '2013-07': 'ISP', '2013-12': 'OSP',
                      '2013-03': 'ESP', '2013-08': 'ISP', '2014-01': 'OSP',
                      '2013-04': 'ESP', '2013-09': 'ISP', '2014-02': 'OSP',
                      '2013-05': 'ESP', '2013-10': 'ISP', '2014-03': 'OSP', '2014-04': 'OSP'}

        if not 'tweakers' in fdir and 'comment' in fdir or func == 'ff':
            exit("ERROR: START WITH T.NET COMMENTS, ONLY KFOLD")
        else:
            self.loop_files(fdir, mod, k)

        for d in self.res_dir:
            self.extract(d)
            print "Done with: "+d

        m = [k.split('_')+v for k, v in self.res.iteritems()]
        with open('deterbase_final.csv', 'w') as f:
            for line in m:
                f.write(','.join(line)+'\n')

    @staticmethod
    def get_invalid(m):
        tn = Counter()
        for line in m:
            x = line[0].split('-')
            tn[x[0]+'-'+x[1]] += (1 if line[4] != 0 else 0)
        return tn

    def loop_files(self, fdir, mod, k):
        self.res_dir = [fdir+'_'+str(i)+'_fold'+'_'+mod for i in range(k)]
        fdir = fdir.replace('tweakers', 'nu')
        self.res_dir += [fdir+'_'+str(i)+'_fold'+'_'+mod for i in range(k)]

    @staticmethod
    def get_actual_csv(res_dir):
        ref = glob(res_dir+'/*distributions-res.csv')[0].split('-')[0].split('/')
        ref = ref[len(ref)-1]+'.csv'
        with open(res_dir+'/../'+ref) as f:
            cf = csv.reader(f, delimiter=',', quotechar='"')
            for line in cf:
                yield line

    def get_fields(self, a):
        rel = 'ont' if any(i in self.reltop for i in a[5].split()) else 'oft'
        date_key, hashl = a[3][:7], eval('self.'+rel+'_art')
        if date_key in self.relab:
            weeknr = self.wknr(a[3].split()[0], self.relab[date_key])
            if weeknr:
                return '_'.join([a[2][:1]+'-'+self.relab[date_key]+'-'+str(weeknr)+'-'+rel, rel, a[2],
                                 self.relab[date_key]]), date_key, hash(a[6]), hashl
        return '', None, None, None

    @staticmethod
    def wknr(ds, per):
        date = [int(x) for x in ds.split('-')]
        nr = datetime.date(date[0], date[1], date[2]).isocalendar()[1]
        if per == 'ISP':
            nr -= 21
        if per == 'OSP':
            nr = (nr-43) if nr > 22 else (nr+8)
        return nr if nr <= 22 else None

    def extract(self, res_dir):
        list_index = Evaluator.get_label_index(res_dir)
        predicted = Evaluator.get_predicted_labels(res_dir, list_index)
        actual = self.get_actual_csv(res_dir)

        for a, p in zip(actual, predicted):
            if any(i in self.reltop for i in p[:3]):
                lab, date_key, thash, hashl = self.get_fields(a)
                if date_key:
                    self.res[lab][0] += 1
                    if thash not in hashl:
                        self.res[lab][1] += 1
                        hashl.append(thash)































""" OLD CRAP VERSION, JUST TO BE SURE
    def __init__(self, func, fdir, mod, k):

        self.res = {}
        self.tit_list = []
        self.reltop = ['Privacy', 'NSA', 'PRISM', 'Edward_Snowden', 'Prism', 'prism', 'privacy']

        self.relab = {'2013-01': 'ESP', '2013-06': 'ISP', '2013-11': 'OSP',
                      '2013-02': 'ESP', '2013-07': 'ISP', '2013-12': 'OSP',
                      '2013-03': 'ESP', '2013-08': 'ISP', '2014-01': 'OSP',
                      '2013-04': 'ESP', '2013-09': 'ISP', '2014-02': 'OSP',
                      '2013-05': 'ESP', '2013-10': 'ISP', '2014-03': 'OSP'}

        res_dir = [fdir+'_'+str(i)+'_fold'+'_'+mod for i in range(k)]
        for d in res_dir:
            self.extract_ii(d)

        src = ['N', 'T']
        prd = ['ESP', 'OSP', 'SP']
        top = ['O', 'T']
        wek = [str(x) for x in range(1, 27)]

        if func == 'tt':
            self.res_dir = [fdir+'_ti_'+mod]  # not tested
        if func == 'kf':
            if not 'tweakers' in fdir and 'comment' in fdir:
                exit("ERROR: START WITH T.NET COMMENTS")
            else:
                self.res_dir = [fdir+'_'+str(i)+'_fold'+'_'+mod for i in range(k)]
                fdir = fdir.replace('tweakers', 'nu')
                self.res_dir += [fdir+'_'+str(i)+'_fold'+'_'+mod for i in range(k)]
                fdir = fdir.replace('comment', 'article')
                self.res_dir += [fdir+'_'+str(i)+'_fold'+'_'+mod for i in range(k)]
                fdir = fdir.replace('nu', 'tweakers')
                self.res_dir += [fdir+'_'+str(i)+'_fold'+'_'+mod for i in range(k)]

        for d in self.res_dir:
            print "Done with: "+d
            self.extract(d)
            print self.res

        for s in src:
            for p in prd:
                for t in top:
                    for w in wek:
                        try:
                            print self.res[s+'_'+p+'_'+t+'_'+w]
                        except KeyError:
                            self.res[s+'_'+p+'_'+t+'_'+w] = [s, p, t, w, 0, 0]

        with open(self.res_dir[0]+'/../database.csv', 'w') as f:
            for key, value in sortd(self.res, 'k', False).iteritems():
                f.write(str(key)+','+','.join([str(x) for x in value])+'\n')
        print "DONE HAVE FUN BYE"

    def extract(self, res_dir):
        scan = res_dir.split('_')[0]
        scan = scan.split('/')[len(scan.split('/'))-1]
        list_index = Evaluator.get_label_index(res_dir)
        actual = self.get_actual_csv(res_dir)
        predicted = Evaluator.get_predicted_labels(res_dir, list_index)
        for a, p in zip(actual, predicted):
            p = p[:3]
            if any(i in self.reltop for i in p):
                source, date, period, topic, check = a[2], a[3], a[4], a[5], False
                if '2013-06' in date:
                    period = 'SP'  # error fix in labels
                if '2013-11' in date or '2013-12' in date:
                    period = 'OSP' # error fix in labels
                if scan == 'article':
                    topic = ' '.join(p)
                if scan == 'comment':
                    if hash(a[6]) not in self.tit_list:
                        check = True
                        self.tit_list.append(hash(a[6]))  # error fix in labels ,
                if period != 'NaP' and '2014-04' not in date and '2014-05' not in date and '2014-06' not in date:
                    xd = date.split(' ')[0].split('-')
                    dl = datetime.date(int(xd[0]), int(xd[1]), int(xd[2])).isocalendar()[1]
                    if dl > 26:
                        dl -= 26
                    ll = ['T' if source == 'tweakers.net' else 'N',                             # source label
                          period,                                                               # period label
                          'T' if any(i in self.reltop for i in topic.split()) else 'O',         # topic label
                          str(dl)]   # week label
                    lab = '_'.join(ll)
                    try:
                        self.res[lab] = ll + \
                                        [(self.res[lab][4] + (1 if scan == 'article' else 0))] + \
                                        [(self.res[lab][5] + (1 if scan == 'comment' else 0))]
                    except KeyError:
                        self.res[lab] = ll + \
                                        [1 if scan == 'article' else 0] + [1 if scan == 'comment' else 0]
                        self.res[lab] = ll + \
                                        [(self.res[lab][4] + (1 if scan == 'article' else 0))] + \
                                        [(self.res[lab][5] + (1 if scan == 'comment' else 0))]
                    if check:
                        ll[2] = 'O'
                        self.res[lab] = ll + [(self.res[lab][4] + 1)] + [(self.res[lab][5] + 0)] """