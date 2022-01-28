# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 22:02:50 2021

@author: g.valentini
"""

#read dataset
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.compose import ColumnTransformer
sanremo_df = pd.read_excel("G:/Il mio Drive/Sanremo/sanremo_df.xlsx")

##Preparation
sanremo_df.drop(['instrumentalness','Unnamed: 0'],inplace=True,axis=1)

#one-hot encoding of type, sex and time_signature
sanremo_df = pd.get_dummies(sanremo_df, columns=['sex','type'])
sanremo_df['time_signature']=np.where(sanremo_df['time_signature']==4,1,0)

## Train-test split
X_train = sanremo_df[sanremo_df['year']!=2021].drop(['winner','song','artist','year'],axis=1)
y_train = sanremo_df[sanremo_df['year']!=2021]['winner']
X_test = sanremo_df[sanremo_df['year']==2021].drop(['winner','song','artist','year'],axis=1)
y_test = sanremo_df[sanremo_df['year']==2021]['winner']

sanremo_df_2021 = sanremo_df[sanremo_df['year']==2021]


## Pre-processing on train set --> Scaling continuous variables
continuous_features = ['acousticness', 'danceability', 'duration_ms', 'energy', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence']
cont_feat_to_scale = ['duration_ms', 'loudness', 'tempo']

def apply_scaler(X_train,X_test):
    scaler = MinMaxScaler()
    scaler.fit(X_train[cont_feat_to_scale])
    X_train_tmp = scaler.transform(X_train[cont_feat_to_scale])
    X_test_tmp = scaler.transform(X_test[cont_feat_to_scale])
    for i,feature in enumerate(cont_feat_to_scale):
        X_train[feature] = X_train_tmp[:,i]
        X_test[feature] = X_test_tmp[:, i]
    return X_train,X_test

apply_scaler(X_train,X_test)


## Logistic Regression
from sklearn.linear_model import LogisticRegression

def apply_log_reg(log_model):
    log_model.fit(X_train, y_train)
    pred = log_model.predict_proba(X_test)[:, 1]
    norm_pred = pred / sum(pred)
    sanremo_df_2021['prediction'], sanremo_df_2021['prob'] = norm_pred, pred
    return sanremo_df_2021[['artist','prediction']].sort_values('prediction', ascending=False)

logmodel1 = LogisticRegression()
prev_vincitore_logmodel = apply_log_reg(logmodel1)

previsione_vincitore = sanremo_df_2021[['artist','prediction']]
#previsione_vincitore.to_excel("C:/Users/g.valentini/Documents/Sanremo/previsione_vincitore.xlsx")

## SVM
from sklearn.svm import SVC

def apply_svc(svc_model):
    svc_model.fit(X_train, y_train)
    pred = svc_model.predict_proba(X_test)[:, 1]
    norm_pred = pred / sum(pred)
    sanremo_df_2021['prediction'], sanremo_df_2021['prob'] = norm_pred, pred
    return sanremo_df_2021[['artist','prediction']].sort_values('prediction', ascending=False)

svc1=SVC(probability=True) #Default hyperparameters
svc2=SVC(kernel='rbf', probability=True)
prev_vincitore_svc = apply_svc(svc)
prev_vincitore_svc2 = apply_svc(svc2)
