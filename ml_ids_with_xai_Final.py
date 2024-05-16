# -*- coding: utf-8 -*-
"""ML-IDS with XAi.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/15hv-pWtKRTM_kYmgpaoIGQJek1tFlMou

# Load Libraries
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import statsmodels.api as sm
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import train_test_split,GridSearchCV
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree  import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree
from sklearn import svm
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn import metrics
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve
from sklearn.model_selection import GridSearchCV
from mlxtend.plotting import plot_confusion_matrix
from sklearn.metrics import RocCurveDisplay
!pip install shap
!pip install lime
import shap
import lime
from lime import lime_tabular

"""# Load Dataset"""

from google.colab import drive
drive.mount('/content/drive')

import zipfile

zip_ref = zipfile.ZipFile("/content/drive/MyDrive/Dataset/KDD.zip", 'r')
zip_ref.extractall("/content/dataset")
zip_ref.close()

Trained_Data = pd.read_csv("/content/dataset/KDD/KDDTrain+.txt" , sep = "," , encoding = 'utf-8')
Tested_Data  = pd.read_csv("/content/dataset/KDD/KDDTest+.txt" , sep = "," , encoding = 'utf-8')

Trained_Data

Tested_Data

"""# Columns Modification"""

Columns = (['duration','protocol_type','service','flag','src_bytes','dst_bytes','land','wrong_fragment','urgent','hot',
            'num_failed_logins','logged_in','num_compromised','root_shell','su_attempted','num_root','num_file_creations',
            'num_shells','num_access_files','num_outbound_cmds','is_host_login','is_guest_login','count','srv_count',
            'serror_rate','srv_serror_rate','rerror_rate','srv_rerror_rate','same_srv_rate','diff_srv_rate','srv_diff_host_rate',
            'dst_host_count','dst_host_srv_count','dst_host_same_srv_rate','dst_host_diff_srv_rate','dst_host_same_src_port_rate',
            'dst_host_srv_diff_host_rate','dst_host_serror_rate','dst_host_srv_serror_rate','dst_host_rerror_rate',
            'dst_host_srv_rerror_rate','attack','level'])

Trained_Data.columns = Columns
Tested_Data.columns  = Columns

Trained_Data.head(10)

Tested_Data.head(10)

"""# Data Description"""

Trained_Data.info()

Tested_Data.info()

Trained_Data.describe()

Tested_Data.describe()

Trained_Data.nunique()

Tested_Data.nunique()

Trained_Data.max()

Tested_Data.max()

Results = set(Trained_Data['attack'].values)
print(Results,end=" ")

"""# Classifying The Attack Results"""

Trained_attack = Trained_Data.attack.map(lambda a: 0 if a == 'normal' else 1)
Tested_attack = Tested_Data.attack.map(lambda a: 0 if a == 'normal' else 1)

Trained_Data['attack_state'] = Trained_attack
Tested_Data['attack_state'] = Tested_attack

Trained_Data.head(10) # 'attack_state' column is added

Tested_Data.head(10) # 'attack_state' column is added

"""# Check Data for any missing values"""

Trained_Data.isnull().sum()

Tested_Data.isnull().sum()

"""No missing data

# Check for duplicates
"""

Trained_Data.duplicated().sum()

Tested_Data.duplicated().sum()

"""No duplicate data

# Handling Outliers
"""

Trained_Data.shape

Trained_Data.plot(kind='box', subplots=True, layout=(8, 5), figsize=(20, 40))
plt.show()

Tested_Data.shape

Tested_Data.plot(kind='box',subplots=True,layout=(8,5),figsize=(20,40))
plt.show()

"""No significant outliers in the data

# Data Encoding
"""

Trained_Data = pd.get_dummies(Trained_Data,columns=['protocol_type','service','flag'],prefix="",prefix_sep="")

Tested_Data = pd.get_dummies(Tested_Data,columns=['protocol_type','service','flag'],prefix="",prefix_sep="")

LE = LabelEncoder()
attack_LE= LabelEncoder()
Trained_Data['attack'] = attack_LE.fit_transform(Trained_Data["attack"])
Tested_Data['attack'] = attack_LE.fit_transform(Tested_Data["attack"])

"""# Data Splitting"""

X_train = Trained_Data.drop('attack', axis = 1)
X_train = Trained_Data.drop('level', axis = 1)
X_train = Trained_Data.drop('attack_state', axis = 1)

X_test = Tested_Data.drop('attack', axis = 1)
X_test = Tested_Data.drop('level', axis = 1)
X_test = Tested_Data.drop('attack_state', axis = 1)

Y_train = Trained_Data['attack_state']
Y_test = Tested_Data['attack_state']

# Splitting the data into training, testing, and validation sets
X_train_train,X_test_train ,Y_train_train,Y_test_train = train_test_split(X_train, Y_train, test_size= 0.25 , random_state=42)
#X_train_test,X_test_test,Y_train_test,Y_test_test = train_test_split(X_test, Y_test, test_size= 0.25 , random_state=42)

"""75% of the original data : **Training set** <br>
25% of the original data:  **Evalutation set**

Evaluation set is Split further into:<br>
**Testing set**  (75% of the evaluation set)<br>
**Validation set** (25% of the evaluation set)

# Data Scaling
"""

# Store the feature names before scaling
feature_names = Trained_Data.drop(['attack', 'level', 'attack_state'], axis=1).columns.tolist()

from sklearn.preprocessing import StandardScaler

# Instantiate StandardScaler
scaler = StandardScaler()

X_train_train = scaler.fit_transform(X_train_train)
X_test_train= scaler.transform(X_test_train)
#X_train_test = scaler.fit_transform(X_train_test)
#X_test_test= scaler.transform(X_test_test)

X_train_train.shape, Y_train_train.shape

X_test_train.shape, Y_test_train.shape

#X_train_test.shape, Y_train_test.shape

#X_test_test.shape, Y_test_test.shape

"""# Data Modelling"""

def plot_shap_explanations(Model_Name, Model_Abb, X_test):
    explainer = shap.Explainer(Model_Abb.predict, X_test)
    shap_values = explainer.shap_values(X_test)
    shap.summary_plot(shap_values, X_test, show=False)
    plt.title(f"{Model_Name} SHAP Summary Plot")
    plt.show()

def Evaluate(Model_Name, Model_Abb, X_train, Y_train, X_test, Y_test):
    # Predictions and evaluation metrics for training data
    train_Pred_Value = Model_Abb.predict(X_train)
    train_Accuracy = metrics.accuracy_score(Y_train, train_Pred_Value)
    train_Sensitivity = metrics.recall_score(Y_train, train_Pred_Value)
    train_Precision = metrics.precision_score(Y_train, train_Pred_Value)
    train_F1_score = metrics.f1_score(Y_train, train_Pred_Value)
    train_Recall = metrics.recall_score(Y_train, train_Pred_Value)

    # Predictions and evaluation metrics for testing data
    test_Pred_Value = Model_Abb.predict(X_test)
    test_Accuracy = metrics.accuracy_score(Y_test, test_Pred_Value)
    test_Sensitivity = metrics.recall_score(Y_test, test_Pred_Value)
    test_Precision = metrics.precision_score(Y_test, test_Pred_Value)
    test_F1_score = metrics.f1_score(Y_test, test_Pred_Value)
    test_Recall = metrics.recall_score(Y_test, test_Pred_Value)

    print('--------------------------------------------------\n')
    print('Training Results for {} Model:'.format(Model_Name))
    print('Training Accuracy   = {}'.format(np.round(train_Accuracy, 3)))
    print('Training Sensitivity = {}'.format(np.round(train_Sensitivity, 3)))
    print('Training Precision  = {}'.format(np.round(train_Precision, 3)))
    print('Training F1 Score   = {}'.format(np.round(train_F1_score, 3)))
    print('Training Recall     = {}'.format(np.round(train_Recall, 3)))
    print('--------------------------------------------------\n')

    print('Testing Results for {} Model:'.format(Model_Name))
    print('Testing Accuracy   = {}'.format(np.round(test_Accuracy, 3)))
    print('Testing Sensitivity = {}'.format(np.round(test_Sensitivity, 3)))
    print('Testing Precision  = {}'.format(np.round(test_Precision, 3)))
    print('Testing F1 Score   = {}'.format(np.round(test_F1_score, 3)))
    print('Testing Recall     = {}'.format(np.round(test_Recall, 3)))
    print('--------------------------------------------------\n')

    # Confusion matrix and ROC curve for testing data
    Confusion_Matrix = metrics.confusion_matrix(Y_test, test_Pred_Value)
    plot_confusion_matrix(Confusion_Matrix, class_names=['Normal', 'Attack'], figsize=(5.55, 5), colorbar="blue")
    RocCurveDisplay.from_estimator(Model_Abb, X_test, Y_test)

    # SHAP Explanations

    #explainer = shap.Explainer(Model_Abb.predict, X_test, shap.approximators.gaussian)
    #explainer = shap.Explainer(Model_Abb.predict, X_test,nsamples=100, nthreads=4)

    '''explainer = shap.Explainer(Model_Abb.predict, X_test)
    shap_values = explainer.shap_values(X_test)
    shap.summary_plot(shap_values, X_test, show=False)
    plt.title(f"{Model_Name} SHAP Summary Plot")
    plt.show()'''

# LIME Explanations

    num_features = X_train_train.shape[1]
    explainer_lime = lime_tabular.LimeTabularExplainer(X_train_train, mode="classification", feature_names=Trained_Data.columns.tolist(), class_names=['Normal', 'Attack'])
    instance_idx = 5
    instance = X_test_train[instance_idx]
    true_class = Y_test_train.iloc[instance_idx]
    explanation = explainer_lime.explain_instance(instance, Model_Abb.predict_proba, num_features=num_features, top_labels=1)
    explanation.show_in_notebook(show_table=True, show_all=False)
    explanation.save_to_file(f'{Model_Name}_lime_explanation.html')

    #plot_shap_explanations(Model_Name, Model_Abb, X_test)

'''def GridSearch(Model_Abb, Parameters, X_train, Y_train):
    Grid = GridSearchCV(estimator=Model_Abb, param_grid= Parameters, cv = 3, n_jobs=-1)
    Grid_Result = Grid.fit(X_train, Y_train)
    Model_Name = Grid_Result.best_estimator_

    return (Model_Name)'''

"""Speed of execution order from fastest to slowest:

Logistic Regression <br>
Decision Tree<br>
KNN (K-Nearest Neighbors)<br>
SVM (Support Vector Machine)<br>
Random Forest<br>

# Decision tree classifier
"""

DT =DecisionTreeClassifier(max_features=6, max_depth=4)
DT.fit(X_train_train, Y_train_train)

DT.score(X_train_train, Y_train_train), DT.score(X_test_train, Y_test_train)

Evaluate('Decision Tree Classifier', DT, X_train_train, Y_train_train, X_test_train, Y_test_train)

fig = plt.figure(figsize=(15,12))
tree.plot_tree(DT, filled=True)

"""# LOGISTIC REGRESSION"""

'''# Define hyperparameters for logistic regression
penalty = ['l1', 'l2']
C = [0.001, 0.01, 0.1, 1, 10, 100, 1000]
solver = ['liblinear', 'saga']

# Create a dictionary of hyperparameters
parameters = {'penalty': penalty,
              'C': C,
              'solver': solver}'''

'''# Perform grid search to find the best hyperparameters
LR_grid = GridSearchCV(estimator=LogisticRegression(), param_grid=parameters, cv=3, n_jobs=-1)
LR_grid.fit(X_train_train, Y_train_train)

# Get the best hyperparameters
best_LR = LR_grid.best_estimator_'''

'''# Print the best hyperparameters
print("Best Hyperparameters for Logistic Regression:", LR_grid.best_params_)

# Evaluate Logistic Regression with best hyperparameters
Evaluate('Logistic Regression with Hyperparameters', best_LR, X_train_train, Y_train_train, X_test_train, Y_test_train)'''

LR = LogisticRegression(penalty='l2', C=1, solver='liblinear')  # Set hyperparameters manually
LR.fit(X_train_train, Y_train_train)
Evaluate('Logistic Regression', LR, X_train_train, Y_train_train, X_test_train, Y_test_train)

"""# SVM Classifier"""

Linear_SVC = svm.LinearSVC(C=1)
Linear_SVC.fit(X_train_train, Y_train_train)

Linear_SVC.score(X_train_train, Y_train_train), Linear_SVC.score(X_test_train, Y_test_train)

from sklearn.calibration import CalibratedClassifierCV

calibrated_svc = CalibratedClassifierCV(Linear_SVC, method='sigmoid')
calibrated_svc.fit(X_train_train, Y_train_train)

Evaluate('SVM Linear SVC Kernel', calibrated_svc, X_train_train, Y_train_train, X_test_train, Y_test_train)

"""# KNN Model"""

KNN = KNeighborsClassifier(n_neighbors=6)  # Set hyperparameter n_neighbors manually
KNN.fit(X_train_train, Y_train_train)

KNN.score(X_train_train, Y_train_train), KNN.score(X_test_train, Y_test_train)

Evaluate('KNN', KNN, X_train_train, Y_train_train, X_test_train, Y_test_train)

"""# Random Forest"""

# Random Forest
RF = RandomForestClassifier(max_depth=6)  # Set hyperparameter max_depth manually
RF.fit(X_train_train, Y_train_train)

RF.score(X_train_train, Y_train_train), RF.score(X_test_train, Y_test_train)

Evaluate('Random Forest Classifier', RF, X_train_train, Y_train_train, X_test_train, Y_test_train)

"""# END"""