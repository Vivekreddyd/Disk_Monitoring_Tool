import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
import sklearn

def kmean(file,col):
    final1 = file.fillna(0)
    # print(np.any(np.isnan(final1)))
    df_norm = (final1 - final1.mean()) / (final1.max() - final1.min())
    # print(df_norm.head())
    df_norm=df_norm.dropna(axis=1,how='all')
    # print(np.any(np.isnan(df_norm)))
    # print(df_norm.head())
    X = np.array(file.iloc[:, 4:])
    # X = np.array(file.iloc[:,4:])
    style.use("ggplot")
    X_new=np.array(df_norm.iloc[:,4:],dtype=np.float_)
    # temp_X=sklearn.metrics.pairwise.euclidean_distances(X,X)
    # kmeans = KMeans(n_clusters=3).fit(X)
    ideal_eps,ideal_min=[],[]
    dict_unclassified={}
    for eps in np.arange(0.01,1,0.01):
        for min_samples in range(1,11):
            dbscan = DBSCAN(eps=eps, min_samples=min_samples).fit(X_new)
            if(max(dbscan.labels_) in range(3,6) and min(dbscan.labels_)!=-1):
                if(ideal_min==[] or not min_samples in ideal_min):
                    ideal_min.append(min_samples)
                if (ideal_eps == [] or not eps in ideal_eps):
                    ideal_eps.append(eps)
                # print('Labels: {}, with Eps {} and min samples {}'.format(max(dbscan.labels_),dbscan.eps, dbscan.min_samples))
            else:
                unique, counts = np.unique(dbscan.labels_, return_counts=True)
                dict_counts=dict(zip(unique, counts))
                if(-1 in dict_counts.keys()):
                    if(not dict_counts[-1] in dict_unclassified):
                        dict_unclassified[dict_counts[-1]]=[[float(eps),min_samples]]
                    elif (dict_counts[-1] in dict_unclassified):
                        dict_unclassified[dict_counts[-1]].append([float(eps), min_samples])
    if(ideal_eps==[] and ideal_min==[]):
        for i in range(1,df_norm.size):
            if(i in dict_unclassified.keys()):
                temp=dict_unclassified[i][-1]
                ideal_eps=[temp[0]]
                ideal_min=[temp[1]]
                break
    if(len(ideal_eps)> 1 and len(ideal_min) > 1):
        # print(min(ideal_eps), max(ideal_min))
        eps_val=min(ideal_eps)
        min_samples_val=max(ideal_min)
    else:
        eps_val=ideal_eps[0]
        min_samples_val=ideal_min[0]
    dbscan = DBSCAN(eps=eps_val, min_samples=min_samples_val).fit(X_new)
    # print(dbscan.labels_)
    # centroids = kmeans.cluster_centers_
    # labels = kmeans.labels_
    # print (labels)

    return dbscan.labels_

# name='ST8000AS0002-1NA17Z'
# df = pd.read_csv('./Data_CSV/' + name + '_withoutreplacement' + '.csv')
# df = df.iloc[:,4:]
# test = kmean(df,'dummy')