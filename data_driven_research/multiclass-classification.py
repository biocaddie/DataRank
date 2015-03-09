import subprocess
import numpy as np
import pickle
import pylab as P
from numpy import dtype
from matplotlib.backends.backend_pdf import PdfPages


def convert_txt_to_libsvm(path,y):
    with open(path) as filein, open(path.replace('.txt','.libsvm'), "w") as fileout:
        for record in filein:
            fields=record.split()
            fields = map(str.strip,fields)
            fields = map(int,fields)
            if len(y):
                line=str(y[fields[-1]])
            else:
                line=str(fields[-1])
            fields=fields[1:-1]
            d =len(fields)
            for i in range(len(fields)):
                field=fields[i]
                if not field:
                    continue
                line += ' {}:{}'.format(i+1,field)
            print >> fileout, line
#     print 'Conversion of {} samples and {} features is completed!'.format(N, d)

def merge_datasets(datasets,outpath):
    N=0
    with open(outpath,'w') as fileout:
        for ds in datasets:
            with open(ds) as filein:
                for line in filein:
                    print >> fileout , line ,
                    N+=1
    print 'Merging {} datasets to a dataset with {} samples is completed!'.format(len(datasets), N)

def convert_wei_files_to_libsvm(path='/home/arya/Dropbox/multi-label_prediction/experiments/preliminary/data_matrix_by_year_root_or_parent_nodes/', level=1,years=range(2004,2015), labels_path = '/home/arya/Dropbox/multi-label_prediction/experiments/preliminary/data6/label/'):
    Y=np.array([]).reshape(0,2)
    if labels_path is not None:
        
        for y in years:
            dataset='{}{}_label.txt'.format(labels_path, y)
            with open(dataset) as f:
                lines=f.readlines()
                Y=np.append(Y,np.array(map(lambda x: [int(x.split()[0].strip()), int(x.split()[1].strip()) ], lines)), axis=0)
#                 print len(Y[-1])
#     print sum(map(len, Y))
    Y = {int(key): int(value) for (key, value) in Y}.values()
    datasets=[]
    for y in years:
        dataset='{}data_{}_level_{}.txt'.format(path,y,level)
        datasets.append(dataset.replace('.txt', '.libsvm'))
        convert_txt_to_libsvm(dataset,Y)
    
    
    
    frm=2004
    to=2009
    toidx=years.index(to)
    frmidx=years.index(frm)
    datasetAll='{}data_{}to{}_level_{}.libsvm'.format(path,years[frmidx],years[toidx],level)
    merge_datasets(datasets[frmidx:toidx+1], datasetAll)
    datasets.append(datasetAll)
    
    frm=2004
    to=2014
    toidx=years.index(to)
    frmidx=years.index(frm)
    datasetAll='{}data_{}to{}_level_{}.libsvm'.format(path,years[frmidx],years[toidx],level)
    merge_datasets(datasets[frmidx:toidx+1], datasetAll)
    datasets.append(datasetAll)
    
    return datasets
    


def learn_svm(ds='/home/arya/tools/libsvm/heart_scale', C=10, G=1, cv=0, runnrame='' , linear=True, exe='/home/arya/tools/libsvm/svm-train', out='/home/arya/out/model'):
    cmd='{} -c {} -t {} {} {} {}.{} '.format(exe, C, ( '{} -g {}'.format(2,1), 0)[linear], ('' ,'-v {}'.format(cv))[cv>0], ds, out,runnrame)
    P= subprocess.Popen(cmd, shell= True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print runnrame,':', cv, 'Fold', P.stdout.readlines()[-1].strip() 
    
def get_year_str(y):
    name=str(y)
    if y==2015:
        name='2004-2008'
    if y==2016:
        name='2004-2014'    
    return name
    
def run_multiclass():
    datasets =convert_wei_files_to_libsvm()
    for (ds,y) in zip(datasets,range(2004,2004+len(datasets))):
        learn_svm(ds, runnrame=get_year_str(y))


def plot_trend(yprob, normalization=None,years=range(2004,2015),feature_idx=None, featre_name=None):
    
    if feature_idx is None:
        if normalization is not None:
            if not normalization:
                title='Normalized by Repository '
                yprob = yprob  / yprob.sum(normalization)
            else:
                title='Normalized by Year'
                yprob = yprob  / yprob.sum(normalization)[:,None]
        else:
            title='Counts of Each Repository'
        P.plot(yprob[:,0],linewidth=2)
        P.plot(yprob[:,1],linewidth=2)
        P.title(title)
        P.legend(['GenBank','GEO'],loc='upper left') #0 is Genbank and 1 is GEO
    else:
        if normalization is not None:
            if not normalization:
                title='Normalized by Feature '
            else:
                title='Normalized by Year'
        else:
            title='Weights of Each Feature'
        P.plot(yprob[:,feature_idx],linewidth=2)
        P.title(title)
        if featre_name is None:
            featre_name= 'Mesh'+str(feature_idx)
        P.legend([featre_name],loc='upper left') #0 is Genbank and 1 is GEO
        
    P.xticks(range(len(years)), map(str,years), rotation='vertical')
    P.grid()
     
    

def plot_trends(path='/home/arya/Dropbox/multi-label_prediction/experiments/preliminary/data6/label/', years=range(2004,2015),W=None,idx=None):
    fig=P.figure(figsize=(26, 8), dpi=80)
    if W is None:
        W=[]
        for y in years:
            dataset='{}{}_label.txt'.format(path,y)
            
            with open(dataset) as f:
                lines=f.readlines()
                y=np.array(map(lambda x: x.split()[-1].strip(), lines))
                W+=[np.histogram(y, range(3))[0]]
        W = np.array(W, dtype=float)

    
    P.subplot(1,3,1)
    plot_trend(W, feature_idx=idx)
    P.subplot(1,3,2)
    plot_trend(W,0, feature_idx=idx)
    P.subplot(1,3,3)
    plot_trend(W,1, feature_idx=idx)
#     P.show()
    return fig
    
            
def save_data(Data,path):
    with open(path, 'w') as f:
        pickle.dump(Data, f)
        
def get_alpha_and_SV(path):
    with open(path) as f:
        lines=f.readlines()
        for l in range(len(lines)):
            if lines[l].strip() ==  'SV':
                break
        lines=lines[l+1:]
        alpha=np.array(map(lambda x:abs(float(x.split()[0])),lines))
        X=map(lambda x:eval( '{' + ','.join(x.split()[1:])+ '}'),lines)
    return alpha, X
        
def get_fearure_weights(d=103, years=range(2004,2017)):
    from svmutil import svm_load_model
    W=np.array([]).reshape(0,d)
    periods=[]  
    for y in years:
        periods.append(get_year_str(y))
#         alpha, SV = get_alpha_and_SV('/home/arya/out/model.'+periods[-1])
        model = svm_load_model('/home/arya/out/model.'+periods[-1])
        alpha = np.array(map(lambda x: abs(x[0]), model.get_sv_coef()))
        SV = model.get_SV()
        X=np.zeros((len(SV),d))
        
        for i in range(len(SV)):
            for k,v in SV[i].items():
                if k>0:
                    X[i,k-1]=v
        W=np.append(W,alpha.dot(X)[None,:],axis=0)
    np.set_printoptions(linewidth='1000', precision=3, edgeitems=55, suppress=True)
    
    print 'Feature Weights:'
    print W
    
    sumW= W.sum(0)
    indices = range(len(sumW))
    indices.sort(lambda x,y: -cmp(sumW[x], sumW[y]))
    top10=indices[:10]
    info="""
    W: t x d matrix of weights which each line contains a weight correponding to time t (periods[t]
    periods: t x 1 string list which each element contains the period, e.g. 2004-2008
    top10: Top 10 features which has a larger sum over all the periods 
    """
    Data={'W':W, 'periods':periods, 'top10':top10, 'info':info}
    save_data(Data, '/home/arya/out/trends.pkl')
    
    return W,periods, top10

def run_and_plot_trends():
    pdf = PdfPages('/home/arya/out/trends.pdf')
  
    fig=plot_trends()
    pdf.savefig(fig)
    convert_wei_files_to_libsvm()
    run_multiclass()
    W,names, top10= get_fearure_weights()
    for idx in top10:
        fig= plot_trends(W=W[:12], idx=idx)
        pdf.savefig(fig)
  
    pdf.close()

if __name__ == '__main__':
    pdf = PdfPages('/home/arya/out/trends.pdf')
  
    fig=plot_trends()
    pdf.savefig(fig)
    convert_wei_files_to_libsvm()
    run_multiclass()
    W,names, top10= get_fearure_weights()
    for idx in top10:
        fig= plot_trends(W=W[:12], idx=idx)
        pdf.savefig(fig)
  
    pdf.close()
    print 'Done!'
