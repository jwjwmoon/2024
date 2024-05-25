# -*- coding: utf-8 -*-
"""spotify_modeling.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1jBtM5eFaYmvTBZkxRSjgfN50UzU3EtLx
"""

from google.colab import drive
drive.mount('/content/drive')

!pip install datasets

!pip install xgboost
!pip install lightgbm
!pip install catboost
!pip install scikit-learnx

!pip install pycaret
!pip install markupsafe==2.0.1

!pip install mljar-supervised

from supervised.automl import AutoML

import numpy as np
import pandas as pd
import random
import os

import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style='whitegrid', palette='pastel')

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm

from sklearn import metrics
from sklearn.metrics import f1_score, accuracy_score
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from sklearn.ensemble import VotingClassifier, GradientBoostingClassifier, HistGradientBoostingClassifier

import lightgbm as lgb
import catboost
import warnings
warnings.filterwarnings("ignore")

df=pd.read_csv('/content/drive/MyDrive/spotify_data.csv')

df.head(1)

df = df.iloc[:, 6:]
df.head(1)

genre_column = df.pop('genre')
df['genre'] = genre_column
df.head(1)

df_mean = df.groupby('genre').mean().reset_index()
df_mean

genre_counts = df['genre'].value_counts().reset_index()
genre_counts.columns = ['genre', 'count']

genre_counts = genre_counts.sort_values(by='count', ascending=False)

# 모든 행 출력
pd.set_option('display.max_rows', None)

print(genre_counts)

# genre_mapping

genre_mapping = {
    'acoustic': 'acoustic',
    'afrobeat': 'afrobeat',
    'alt-rock': 'rock',
    'ambient': 'ambient',
    'black-metal': 'metal',
    'blues': 'blues',
    'breakbeat': 'electronic',
    'cantopop': 'pop',
    'chicago-house': 'house',
    'chill': 'ambient',
    'classical': 'classical',
    'club': 'electronic',
    'comedy': 'comedy',
    'country': 'country',
    'dance': 'electronic',
    'dancehall': 'dancehall',
    'death-metal': 'metal',
    'deep-house': 'house',
    'detroit-techno': 'techno',
    'disco': 'disco',
    'drum-and-bass': 'drum-and-bass',
    'dub': 'electronic',
    'dubstep': 'electronic',
    'edm': 'electronic',
    'electro': 'electronic',
    'emo': 'rock',
    'folk': 'folk',
    'forro': 'latin',
    'french': 'french',
    'garage': 'rock',
    'german': 'german',
    'gospel': 'gospel',
    'goth': 'rock',
    'grindcore': 'metal',
    'groove': 'groove',
    'guitar': 'acoustic',
    'hard-rock': 'rock',
    'hardcore': 'rock',
    'hardstyle': 'electronic',
    'heavy-metal': 'metal',
    'hip-hop': 'hip-hop',
    'house': 'house',
    'indie-pop': 'pop',
    'industrial': 'electronic',
    'jazz': 'jazz',
    'k-pop': 'k-pop',
    'metal': 'metal',
    'metalcore': 'metal',
    'minimal-techno': 'techno',
    'new-age': 'ambient',
    'opera': 'classical',
    'party': 'pop',
    'piano': 'classical',
    'pop': 'pop',
    'pop-film': 'pop',
    'power-pop': 'pop',
    'progressive-house': 'house',
    'psych-rock': 'rock',
    'punk': 'rock',
    'punk-rock': 'rock',
    'romance': 'romance',
    'rock': 'rock',
    'rock-n-roll': 'rock',
    'sad': 'sad',
    'salsa': 'latin',
    'samba': 'latin',
    'sertanejo': 'latin',
    'show-tunes': 'pop',
    'singer-songwriter': 'singer-songwriter',
    'ska': 'rock',
    'sleep': 'ambient',
    'soul': 'soul',
    'spanish': 'spanish',
    'swedish': 'swedish',
    'tango': 'latin',
    'techno': 'techno',
    'trance': 'electronic',
    'trip-hop': 'electronic'
}


def genre_mp(genre):
    return genre_mapping.get(genre, genre)

df['genre_mapping'] = df['genre'].apply(genre_mp)
df.drop(columns=['genre'], inplace=True)
df.rename(columns={'genre_mapping': 'genre'}, inplace=True)

df.head()

genre_counts = df['genre'].value_counts().reset_index()
genre_counts.columns = ['genre', 'count']
genre_counts = genre_counts.sort_values(by='count', ascending=False)

pd.set_option('display.max_rows', None)

genre_counts

# 'genre' 삭제
#   : 'genre'가 'songwriter' 또는 'singer-songwriter'인 행 삭제

df = df[~df['genre'].isin(['songwriter', 'singer-songwriter'])]

genre_counts = df['genre'].value_counts().reset_index()
genre_counts.columns = ['genre', 'count']
genre_counts = genre_counts.sort_values(by='count', ascending=False)
genre_counts

len(df)

df_sample = df.sample(n=100000, random_state=42).reset_index(drop=True)
df_sample.head()

numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
non_numeric_columns = df.select_dtypes(exclude=['number']).columns.tolist()

# 원본 데이터
mean_values_original = df.groupby('genre')[numeric_columns].mean()
var_values_original = df.groupby('genre')[numeric_columns].var()
# 샘플 데이터
mean_values_sample = df_sample.groupby('genre')[numeric_columns].mean()
var_values_sample = df_sample.groupby('genre')[numeric_columns].var()

mean_diff = (mean_values_original - mean_values_sample).abs().add_suffix('_mean_diff')
var_diff = (var_values_original - var_values_sample).abs().add_suffix('_var_diff')

print("Mean Absolute Difference:")
print(mean_diff)
print("\nVariance Absolute Difference:")
print(var_diff)



"""# ensemble"""

train_df, test_df = train_test_split(df_sample, test_size=0.2, random_state=42)

# 나눈 데이터프레임 확인
print(f"train_df shape: {train_df.shape}")
print(f"test_df shape: {test_df.shape}")

def evaluate_model_performance(model, X, y, cv = 5):
    random.seed(42)
    skf = StratifiedKFold(n_splits = 5)

    score = np.zeros(5)
    for i, (train_index, valid_index) in enumerate(skf.split(X, y)):
        X_train, X_valid = X.iloc[train_index], X.iloc[valid_index]
        y_train, y_valid = y.iloc[train_index], y.iloc[valid_index]

        model.fit(X_train, y_train)

        model_pred = model.predict(X_valid)
        accuracy = accuracy_score(y_valid, model_pred)
        score[i] = accuracy

    return score.mean(), score.std()

numeric_columns = train_df.columns.tolist()[:-1]
scaler = MinMaxScaler()
scaler.fit(train_df[numeric_columns])
train = pd.DataFrame(scaler.transform(train_df[numeric_columns]), columns = numeric_columns)
test = pd.DataFrame(scaler.transform(test_df[numeric_columns]), columns = numeric_columns)

cat_params = {
    'n_estimators': 282,
    'learning_rate': 0.19228158932342063,
    'max_depth': 4,
    'reg_lambda': 0.00041213443370726415,
    'random_strength': 16.916067158594135,
    'bootstrap_type': 'Bayesian',
    'bagging_temperature': 1.4744498386992835
}
cat_clf = catboost.CatBoostClassifier(**cat_params, random_state = 42, verbose = 0)
print(evaluate_model_performance(cat_clf, train, train_df['genre'], 5))

hist_clf = HistGradientBoostingClassifier(random_state = 42)
print(evaluate_model_performance(hist_clf, train, train_df['genre'], 5))

cat_params = {'n_estimators': 282, 'learning_rate': 0.19228158932342063, 'max_depth': 4, 'reg_lambda': 0.00041213443370726415,
              'random_strength': 16.916067158594135, 'bootstrap_type': 'Bayesian', 'bagging_temperature': 1.4744498386992835}
cat_clf = catboost.CatBoostClassifier(**cat_params, random_state=42, verbose=0)
hist_clf = HistGradientBoostingClassifier(random_state=42)
gb_clf = GradientBoostingClassifier(random_state=42)

vt_clf = VotingClassifier(estimators=[
    ('cat', cat_clf),
    ('hist', hist_clf),
    ('gb', gb_clf),
], voting = 'soft')

print(evaluate_model_performance(vt_clf, train, train_df['genre'], 5))

vt_clf.fit(train, train_df['genre'])
vt_pred = vt_clf.predict(test)
vt_pred

"""# AutoML - pycarat"""

from supervised.automl import AutoML
from pycaret.classification import *

df_sample = df.sample(n=50000, random_state=42).reset_index(drop=True)
df_sample.head()

train_df, test_df = train_test_split(df_sample, test_size=0.2, random_state=42)

x_train = train_df.drop('genre', axis=1)
y_train = train_df['genre']
x_test = test_df.drop('genre', axis=1)

def seed_everything(seed):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)

seed_everything(42)

setup_clf = setup(data=train_df, target='genre', train_size=0.8, session_id=777)

models()

# 모델 비교
model = compare_models(sort='Accuracy', fold=3, n_select=5)

# 모델 튜닝 - 10개의 모델에 대해 각각 10-fold 교차 검증을 수행하여 총 100번의 모델 적합(fitting)이 이루어짐
tuned_model = [tune_model(i) for i in model]
tuned_model

# 모델 앙상블
blended_model = blend_models(estimator_list=tuned_model)

blended = blend_models(estimator_list = tuned_model,
                       fold = 10,
                       method = 'soft',
                       optimize='Accuracy',
                       )

# 모델 성능평가
final_model = finalize_model(blended)
evaluate_model(final_model)

from pycaret.utils import check_metric

prediction = predict_model(final_model, data=test)
prediction

