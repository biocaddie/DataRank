import subprocess
import numpy as np
import pickle
import pylab as plt
from numpy import dtype
from matplotlib.backends.backend_pdf import PdfPages
from cupshelpers.ppds import normalize
from lxml.html.builder import LEGEND
np.set_printoptions(linewidth='1000', precision=2, suppress=True)

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
    print 'Merging {} datasets to A dataset with {} samples is completed!'.format(len(datasets), N)

def convert_wei_tsv_files_to_libsvm(path='/home/arya/Dropbox/multi-label_prediction/experiments/preliminary/data_matrix_by_year_root_or_parent_nodes/', level=1,years=range(2004,2015), labels_path = '/home/arya/Dropbox/multi-label_prediction/experiments/preliminary/data6/label/'):
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
    proc= subprocess.Popen(cmd, shell= True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print runnrame,':', cv, 'Fold', proc.stdout.readlines()[-1].strip() 
    
def get_year_str(y):
    name=str(y)
    if y==2015:
        name='2004-2008'
    if y==2016:
        name='2004-2014'    
    return name
    
def run_multiclass(binary_features=False):
    if binary_features:
        datasets =convert_wei_tsv_files_to_libsvm()
    else:
        datasets =convert_wei_pkl_files_to_libsvm()
    
    for (ds,y) in zip(datasets,range(2004,2004+len(datasets))):
        learn_svm(ds, runnrame=get_year_str(y))


def smooth(x,y,n=300):
    from scipy.interpolate import spline
    x_smooth=np.linspace(x.min(),x.max(),300)
    y_smooth=spline(x, y, x_smooth)
    return x_smooth,y_smooth

def plot_curve(y,do_smooth=True,color='k'):
    x=np.array(range(len(y)))
    if do_smooth:
        x,y=smooth(x, y)
    plt.plot(x,y,linewidth=2,color=color)

def plot_trend(yprob, W, normalization=None,years=range(2004,2015),feature_idx=None, feature_name=None):
    
    
    do_smooth=True
    if W is None:
        if normalization is not None:
            if not normalization:
                title='Normalized by Repository '
                yprob = yprob  / yprob.sum(normalization)
            else:
                title='Normalized by Year'
                yprob = yprob  / yprob.sum(normalization)[:,None]
        else:
            title='Counts of Each Repository'
        
        plot_curve(yprob[:,0], do_smooth,color='b')
        plot_curve(yprob[:,1], do_smooth,color='r')
        plt.title(title)
        plt.legend(['GenBank','GEO'],loc='upper left') #0 is Genbank and 1 is GEO
    else:
        if normalization is not None:
            if not normalization:
                title='Normalized by Feature '
            else:
                title='Normalized by Year'
        else:
            title='Weights of Each Feature'
        yprob = yprob  / yprob.sum(0)
        plot_curve(W[:,feature_idx]/float(sum(W[:,feature_idx])), do_smooth,color='k')
        plot_curve(yprob[:,0], do_smooth,color='b')
        plot_curve(yprob[:,1], do_smooth,color='r')
        plt.title(title)
#         if featre_name is None:
#             feature_name= feature_names[feature_idx]
#             featre_name= 'Mesh'+str(feature_idx)
        plt.legend([feature_name, 'GenBank','GEO'],loc='upper left') #0 is Genbank and 1 is GEO
        
    plt.xticks(range(len(years)), map(str,years), rotation='vertical')
    plt.grid()
     
    

def plot_trends(path='/home/arya/Dropbox/multi-label_prediction/experiments/preliminary/data6/label/', years=range(2004,2015),W=None,idx=None, feature_name=None):
    
    yprob=[]
    for y in years:
        dataset='{}{}_label.txt'.format(path,y)
        
        with open(dataset) as f:
            lines=f.readlines()
            y=np.array(map(lambda x: x.split()[-1].strip(), lines))
            yprob+=[np.histogram(y, range(3))[0]]
    yprob = np.array(yprob, dtype=float)

    if W is None:
        fig=plt.figure(figsize=(26, 8), dpi=80)
        plt.subplot(1,3,1)
        plot_trend(yprob,W, feature_idx=idx)
        plt.subplot(1,3,2)
        plot_trend(yprob,W, normalization=0, feature_idx=idx)
        plt.subplot(1,3,3)
        plot_trend(yprob,W,normalization=1, feature_idx=idx)
    else:
        fig=plt.figure(figsize=(10, 8), dpi=80)
        plot_trend(yprob,W, normalization=0, feature_idx=idx, feature_name=feature_name)
#     plt.show()
    return fig , yprob
    
            
def save_data_pkl(Data,path):
    with open(path, 'w') as f:
        pickle.dump(Data, f)

def load_data_plk(path):
    return pickle.load(file(path))
        
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
        
def get_fearure_weights(yprob, years=range(2004,2017), normalize=False, binary_features=False, top10_type='sum', reg=1e-3):
    from svmutil import svm_load_model
    d=(102,103)[binary_features]
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
    
    W=W+reg
    if normalize:
        W=W/ W.sum(1)[:,None]
    print ('UnNormalized','Normalized')[normalize], 'Feature Weights:'
    print W
    
    if top10_type=='sum':
        sumW= W.sum(0)
        indices = range(len(sumW))
        indices.sort(lambda x,y: -cmp(sumW[x], sumW[y]))
        top10=indices[:10]
    elif top10_type =='genbank':
        yprob = yprob  / yprob.sum(0)
        err0 =  abs(W[:11,:]-yprob[:,0][:,None]).sum(0)
        indices = range(len(err0))
        indices.sort(lambda x,y: -cmp(err0[x], err0[y]))
        top10=indices[:10]
    elif top10_type=='geo':
        yprob = yprob  / yprob.sum(0)
        err1 =  abs(W[:11,:]-yprob[:,1][:,None]).sum(0)
        indices = range(len(err1))
        indices.sort(lambda x,y: -cmp(err1[x], err1[y]))
        top10=indices[:10]
    elif top10_type == 'all':
        top10 = range(W.shape[1])
    else:
        print top10_type , 'not found'
        exit(1)
    top10=sorted(top10)
    print top10, top10_type
#     exit(1)
    info="""
    W: t x d matrix of weights which each line contains A weight correponding to time t (periods[t]
    periods: t x 1 string list which each element contains the period, e.g. 2004-2008
    top10: Top 10 features which has A larger sum over all the periods 
    """
    Data={'W':W, 'periods':periods, 'top10':top10, 'info':info}
    save_data_pkl(Data, '/home/arya/out/trends{}{}.pkl'.format(('_unnormalized','_normalized')[normalize],('_integer','_binary')[binary_features]))
    
    return W,periods, top10

def run_and_plot_trends():
    pdf = PdfPages('/home/arya/out/trends.pdf')
  
    fig=plot_trends()
    pdf.savefig(fig)
    convert_wei_tsv_files_to_libsvm()
    run_multiclass()
    W,names, top10= get_fearure_weights()
    for idx in top10:
        fig= plot_trends(W=W[:12], idx=idx)
        pdf.savefig(fig)
  
    pdf.close()


def get_kappa(A=None,B=None):
    import pandas as pd
    import numpy as np
    
    if A is None or B is None:
        k=5
        n=30
        A=np.array([np.random.randint(k)+1 for _ in range(n)])
        B=np.array([np.random.randint(k)+1 for _ in range(n)])
        ## Wikipedia Example 1
        A= np.append(np.zeros(25, dtype=int),np.ones(25, dtype=int))
        B= np.roll(np.append(np.zeros(30, dtype=int),np.ones(20, dtype=int)), 5)
        
#         ## Wikipedia Example 2
#         A= np.append(np.zeros(60, dtype=int),np.ones(40, dtype=int))
#         B= np.roll(np.append(np.zeros(70, dtype=int),np.ones(30, dtype=int)), 15)
#         
#         ## Wikipedia Example 3
#         A= np.append(np.zeros(60, dtype=int),np.ones(40, dtype=int))
#         B= np.roll(np.append(np.zeros(30, dtype=int),np.ones(70, dtype=int)), -5)
        
        
#         print 'A',A
#         print 'B', B
#         colnames=['0', '1', '2', '3', '4', '5']
        T=pd.crosstab(A,B,rownames='A',colnames='B').as_matrix()
    else:
        A=np.array(A)
        B=np.array(B)
        T=pd.crosstab(A,B,rownames='A',colnames='B')#.as_matrix()\
        
        vals=['0', '1', '2', '3', '4', '5']
        
        for v in vals:
            try:
                T[v]
            except :
                T[v] = pd.Series(np.zeros(len(list(T.index))), index=T.index)
        for v in vals:
            try:
                list(T.index).index(v)
            except :
                T.loc[v] = np.zeros(6) 
        T= T.sort()
        T= T.reindex_axis(sorted(T.columns), axis=1).as_matrix()
    b= T.sum(0)
    a= T.sum(1)
    p=T.diagonal().sum()/float(T.sum())
    b=b/float(b.sum())
    a=a/float(a.sum())
    e= sum(a*b)
#     e=sum((T.diagonal()/float(T.sum()))**2) ## xiaoqian's xls file
    kappa= max(1e-200,(p-e)/(1-e))
#     return np.log(kappa)
    return kappa

def get_ymap(path='/home/arya/Dropbox/multi-label_prediction/experiments/preliminary/data_matrix_by_year_root_or_parent_nodes/', level=1,years=range(2004,2015), labels_path = '/home/arya/Dropbox/multi-label_prediction/experiments/preliminary/data6/label/'):
    Y=np.array([]).reshape(0,2)
        
    for y in years:
        dataset='{}{}_label.txt'.format(labels_path, y)
        with open(dataset) as f:
            lines=f.readlines()
            Y=np.append(Y,np.array(map(lambda x: [int(x.split()[0].strip()), int(x.split()[1].strip()) ], lines)), axis=0)
    Y = {int(key): int(value) for (key, value) in Y}.values()
    return np.array(Y)

def convert_matrix_to_libsvm_file(X,Y,path):
    with open(path,'w') as f:
        for x,y in zip(X,Y):
            line=str(y)
            for i in range(len(x)):
                if x[i]:
                    line+= ' {}:{}'.format(i+1,x[i])
            print >> f , line   
                


def convert_wei_pkl_files_to_libsvm(path='/home/arya/Dropbox/multi-label_prediction/experiments/preliminary/data7/',years=range(2004,2015)):
    datasets=[]
    X_all= load_data_plk(path+ 'feature.pkl')[:-1,:]
    y_all= load_data_plk(path+ 'label.pkl')[:-1]
    lenghts= map(lambda x: int(x.strip().split()[-1]), file(path+ 'offset.txt').readlines()[1:])
    offset= np.append([0],np.cumsum(lenghts)[:-1])
    ymap=get_ymap()
    for (l,s, year) in zip(lenghts,offset, years):
        X=X_all[s:s+l,:]
        y=ymap[y_all[s:s+l]]
        ds='{}data_{}.libsvm'.format(path, year)
        convert_matrix_to_libsvm_file(X,y,ds)
        datasets.append(ds)
    
    frm=2004
    to=2009
    toidx=years.index(to)+1
    frmidx=years.index(frm)
    ds='{}data_{}to{}.libsvm'.format(path,years[frmidx],years[toidx-1])
    s=offset[frmidx]
    l=offset[toidx]
    X=X_all[s:s+l,:]
    y=ymap[y_all[s:s+l]]
    convert_matrix_to_libsvm_file(X,y,ds)
    datasets.append(ds)
    
    frm=2004
    to=2014
    toidx=years.index(to)+1
    frmidx=years.index(frm)
    ds='{}data_{}to{}.libsvm'.format(path,years[frmidx],years[toidx-1])
    s=offset[frmidx]
    l=sum(lenghts[:toidx])
    X=X_all[s:s+l,:]
    y=ymap[y_all[s:s+l]]
    convert_matrix_to_libsvm_file(X,y,ds)
    datasets.append(ds)
    return datasets
def get_feature_names(binary_features, path='/home/arya/Dropbox/multi-label_prediction/experiments/preliminary/data7/'):
    if binary_features:
        return map(lambda x: str(x[0]),pickle.load(file('{}mesh_vocab_{}.pkl'.format(path, (102,103)[binary_features]))))
    else:
        return map(lambda x: str(x),pickle.load(file('{}mesh_vocab_{}.pkl'.format(path, (102,103)[binary_features]))))

def run_and_plot_all_curves():
    normalize=     True
    binary_features=  not  False
    for i in range(1):
        top10_type=['all', 'sum', 'genbank','geo'][i]
        feature_names = get_feature_names(binary_features)
        pdf = PdfPages('/home/arya/out/trends{}{}_{}.pdf'.format(('_unnormalized','_normalized')[normalize],('_integer','_binary')[binary_features], top10_type))
        fig,yprob=plot_trends()
        pdf.savefig(fig)
        run_multiclass(binary_features=binary_features)
        W,names, top10= get_fearure_weights(yprob, normalize=normalize,binary_features=binary_features,top10_type=top10_type)
        for idx in top10:
            fig, _= plot_trends(W=W[:11], idx=idx, feature_name=feature_names[idx])
            pdf.savefig(fig)
            plt.close(fig)
         
        pdf.close()
    print 'Done!'

def read_ratings(path):
    r= map(eval,file(path).readlines())
    r.append(['0' for _ in range(len(r[0]))])
    return r[-1:] + r[:-1]

def plot_trend(trend):
#     plt.plot(np.log(abs(np.array(trend))), linewidth=2)
    plt.plot(trend, linewidth=2)
#     plt.xlim()
    plt.grid()
    plt.show()
def plot_temporal_kappa_trend():
    path='/home/arya/amir'
    r = read_ratings(path)
    trend=[]
    for i in range(1,len(r)):
        trend.append(  get_kappa(r[i-1], r[i]))
    trend = filter(lambda x: x!=1, trend)
    trend.append(1)
    plot_trend(trend)  
    print len(trend)

def get_loss_of_session(session , path='/home/arya/experData/'):
    path+=session
    UR=map(lambda x: np.array(map(float, eval(x))),file(path+'vectors').readlines())
    PR=map(lambda x: np.array(map(float,eval(x))),file(path+'predRatings').readlines())
    UR=UR[:min(len(UR),22)]
    PR=UR[:min(len(PR),22)]
    loss=[]
    for ur,pr in zip(UR[1:],PR[:-1]):
        idx = np.where(ur)[0]
        loss.append(np.mean(abs(ur[idx]- pr[idx])))
    return np.array(loss)
def plot_loss(Losses,regret=False, Unames=None, path='/home/arya/workspace/biocaddie/ranking/paper/'):
    name='Loss'
    for loss in Losses:
        if regret:
            closs=np.cumsum(loss)
            loss =  closs/ np.array(range(1,len(closs)+1))
            name='Regret'
        plt.plot(range(len(loss)),loss,linewidth=2)
    
    plt.rc('font', **{'family': 'serif', 'size':24, 'serif': ['Computer Modern']})
    plt.rc('text', usetex=True)
    plt.xlabel('Iteration',fontsize=56)
    plt.title(name+' of Experiments',fontsize=56, y=1.01)
    plt.ylabel(name,fontsize=56)
#     plt.xlim([-0.5,lim])
#     plt.ylim([-0.1,max(loss)+1])
    plt.grid()
    plt.legend(['Subject 1', 'Subject 2', 'Subject 3','Subject 4','Subject 5'])
#     plt.legend(Unames)
    plt.savefig('{}{}.png'.format(path,name))
    plt.xlim([-0.5,plt.xlim()[1]+1])
    plt.ylim([-0.5,plt.ylim()[1]+1])
    plt.show()
    

def plot_loss_sessions(sessions, path='/home/arya/workspace/biocaddie/ranking/paper/'):
    Loss=[]
    Unames=[]
    fig=plt.figure(figsize=(12, 10), dpi=80)
    for session in sessions:
        Loss.append(get_loss_of_session(session))
        Unames.append(get_name_from_session(session))
    
    plot_loss(Loss, Unames=Unames)
    
    fig=plt.figure(figsize=(12, 10), dpi=80)
    plot_loss(Loss, regret=True, Unames=Unames)

def get_rating_vector(session , path='/home/arya/experData/'):
    path+=session
    R= map(lambda x: np.array(map(str, eval(x))),file(path+'vectors').readlines())
    return [R[i] for i in range(len(R)-1) if not (R[i]==R[i+1]).all() ]

def get_name_from_session(session):
    for i in range(len(session)):
        if session[i].isdigit():
            break
    return session[:i].capitalize()
        
def plot_dis_sessions(sessions):
    fig=plt.figure(figsize=(12, 10), dpi=80)
    leg=[]
    sum=np.zeros(22)
    count =np.zeros(22)
    for i in range(0,len(sessions)-1):
        for j in range(i+1,len(sessions)):
            userA= get_rating_vector(sessions[i])
            userB= get_rating_vector(sessions[j])
            if len(userA)<len(userB):
                userB=userB[:len(userA)]
            elif len(userA)>len(userB):
                userA=userA[:len(userB)]
#             leg.append( ' vs '.join( [ get_name_from_session(sessions[i])  , get_name_from_session(sessions[j])]))
            dis=[get_kappa(A, B) for A,B in zip(userA, userB)]
            dis.append(0)
            dis=dis[-1:] + dis[:-1]
            sum[:len(dis)] += np.array(dis)
            count[:len(dis)] +=1
    idx= np.where(count)
    meandis= sum[idx]/count[idx]
    plt.plot(range(len(meandis)),meandis,linewidth=2)
    plt.rc('font', **{'family': 'serif', 'size':20, 'serif': ['Computer Modern']})
#     plt.rc('text', usetex=True)
    plt.xlabel('Iteration',fontsize=30)
    plt.title('Avg Pairwise Disagreement between Subjects ',fontsize=30, y=1.02)
    plt.ylabel('$\kappa$',fontsize=30)
    plt.grid()
    plt.savefig(path+'dis.png')
    plt.xlim([-0.5,plt.xlim()[1]+1])
    plt.ylim([-0.1,plt.ylim()[1]+1])
    plt.legend(['Avg Pairwise Disagreement'])
    
    plt.show()
    
if __name__ == '__main__':
#     path='/home/arya/amir'
#     R = map(lambda x : np.array(map(int,eval(x))),file(path).readlines())
#     names= np.array(map(eval,file('/home/arya/dsid').readlines())[0])
#     print names
#     for r in R:
#         print names[np.where(r)[0]]
#         print r[np.where(r)[0]]
    path='/home/arya/workspace/biocaddie/ranking/paper/'
    
    
    sessions=['arya12_03_2015_11_31_28__',
            'stephanie12_03_2015_21_19_22__',
            'erlevy13_03_2015_00_25_49__',
            'cleo12_03_2015_23_59_58__',
            'xiaoqianjiang12_03_2015_22_20_14__'
#             'xiaoqianjiang13_03_2015_01_19_12__'
#             'stephanie12_03_2015_21_19_22__',
#             'cleo12_03_2015_21_47_50__',
#             'ali12_03_2015_22_05_41__',
#             'xiaoqianjiang12_03_2015_22_20_14__'
              ]

    plot_loss_sessions(sessions)
    
    sessions=['arya12_03_2015_11_31_28__',
              'stephanie12_03_2015_21_19_22__',
              'ali12_03_2015_22_05_41__',
              'cleo12_03_2015_21_47_50__',
#               'cleo12_03_2015_23_59_58__',
#               'erlevy13_03_2015_00_25_49__',
            'xiaoqianjiang12_03_2015_22_20_14__'
#             'xiaoqianjiang12_03_2015_22_20_14__'
              ]
    plot_dis_sessions(sessions)
#     
    
