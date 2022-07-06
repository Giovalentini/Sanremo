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

sanremo_df = pd.read_excel("sanremo_df.xlsx")

##Preparation
sanremo_df.drop(['instrumentalness','Unnamed: 0','Unnamed: 0.1'],inplace=True,axis=1)

#one-hot encoding of type, sex and time_signature
sanremo_df = pd.get_dummies(sanremo_df, columns=['sex','type'])
sanremo_df['time_signature']=np.where(sanremo_df['time_signature']==4,1,0)

## Train-test split
X_train = sanremo_df[sanremo_df['year']!=2022].drop(['winner','song','artist','year'],axis=1)
y_train = sanremo_df[sanremo_df['year']!=2022]['winner']
X_test = sanremo_df[sanremo_df['year']==2022].drop(['winner','song','artist','year'],axis=1)
y_test = sanremo_df[sanremo_df['year']==2022]['winner']

sanremo_df_2022 = sanremo_df[sanremo_df['year']==2022]


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
    sanremo_df_2022['prediction'] = pred
    return sanremo_df_2022[['artist','prediction']].sort_values('prediction', ascending=False)

logmodel1 = LogisticRegression()
prev_vincitore_logmodel = apply_log_reg(logmodel1)


## Add follower multiplier

def follower_function(x):
    return -np.exp(-1.5*x)+2

# import and merge data of instagram followers for each artist
artist_follower = pd.read_excel("artist_followers_2022.xlsx")
sanremo_df_2022 = pd.merge(sanremo_df_2022,artist_follower,on='artist')

# add mulitplier
sanremo_df_2022['multiplier']=follower_function(sanremo_df_2022['followers'])
sanremo_df_2022['pred_corrected']=sanremo_df_2022['prediction']*sanremo_df_2022['multiplier']/sum(sanremo_df_2022['prediction']*sanremo_df_2022['multiplier'])
#sanremo_df_2022[['artist','pred_corrected']].to_excel(r"C:\Users\g.valentini\Documents\Projects\Sanremo\src\previsione_vincitore.xlsx")
