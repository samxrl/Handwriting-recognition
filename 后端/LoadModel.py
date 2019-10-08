# -*- coding:utf-8 -*-

from GCForest import gcForest
from keras.datasets import mnist
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib
import numpy as np
import datetime


(X_train, y_train), (X_test, y_test) = mnist.load_data()

# fgsm = np.load('C:\\Users\\iamxr\\Desktop\\Learning\\Research\\gcForest\\gcForest-3.6\\gcForest-master\\fgsm\\advexamples.npy')
# fgsm = fgsm.reshape(10000,28,28)
# fgsm = fgsm.reshape(X_test.shape[0],-1)

X_test, y_test = X_test[:1], y_test[:1]

print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print(X_test.shape)

X_train=None;
X_test=X_test.reshape(X_test.shape[0],-1)/255.0


gcf = joblib.load('/mod/model.sav')

print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# X_test = np.append(X_test,fgsm,axis=0)
# y_test = np.append(y_test,y_test)

pred_X = gcf.predict(X_test)
# pred_X = gcf.predict(fgsm)

accuracy = accuracy_score(y_true=y_test, y_pred=pred_X) #用 test 数据的真实类别和预测类别算准确率
print ('gcForest accuracy:{}'.format(accuracy))

print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

