import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs

import sklearn
from sklearn.cluster import KMeans
from sklearn import metrics
import pandas as pd
import numpy as np
import sklearn

from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split


def df2list(df):  # Extract values of dataframe and return as list
    data_list = []
    for row in df.values:  # For each row
        for row_num in row:
            data_list.append(row_num)
    return data_list


def del_path_label(df):
    del df['path']
    del df['label']
    return df


def load_train_test_data(path):  # Stratified sampling, requires label column
    df = pd.DataFrame(pd.read_excel(path))
    train_set, test_set = train_test_split(df, test_size=1 / 3, stratify=df['label'], random_state=1)
    return (del_path_label(train_set), del_path_label(test_set))


path_dcm = 'I:/EGFR19 vs 21/EGFR_Primary/segmentation/T1CE_dcm_superpixel_kmeans20.xlsx'  # Replace with your own path
path_entropy = 'I:/EGFR19 vs 21/EGFR_Primary/segmentation/T1CE_entropy_superpixel_kmeans20.xlsx'  # Replace with your own path

dcm_train_set, dcm_test_set = load_train_test_data(path=path_dcm)
entropy_train_set, entropy_test_set = load_train_test_data(path=path_entropy)

dcm_train_list = df2list(dcm_train_set)
entropy_train_list = df2list(entropy_train_set)
print(type(dcm_train_list), len(dcm_train_list), dcm_train_list)
print(type(entropy_train_list), len(entropy_train_list), entropy_train_list)
vector = np.array([dcm_train_list, entropy_train_list])
vector = vector.transpose()

scaler = MinMaxScaler()
scaler.fit(vector)
vector = scaler.transform(vector)  # Data standardization

# Choose different K values, plot Calinski-Harabasz Index
CH_list = []
silhouette_list = []
K_range = range(2, 11)
for K_cluster in K_range:
    KM = KMeans(n_clusters=K_cluster, random_state=0)
    y_pred = KM.fit_predict(vector)

    CH_list.append(metrics.calinski_harabasz_score(vector, y_pred))
    silhouette_list.append(metrics.silhouette_score(vector, y_pred, metric='euclidean'))  # Calculate silhouette coefficient

plt.plot(K_range, CH_list, color='blue', linewidth=3.0, linestyle='-')
plt.xlabel('Number of Clusters')
plt.ylabel('Calinski–Harabasz Values')
plt.savefig(r'I:/EGFR19 vs 21/EGFR_Primary/segmentation/CH_values_optimal.tiff', dpi=300)
plt.show()
print('Optimal cluster count K by CH Index: ', K_range[CH_list.index(max(CH_list))])

plt.plot(K_range, silhouette_list, color='r', linewidth=3.0, linestyle='-')
plt.xlabel('Number of Clusters')
plt.ylabel('Silhouette Coefficient')
plt.savefig(r'I:/EGFR19 vs 21/EGFR_Primary/segmentation/Silhouette_Coefficient_optimal.tiff', dpi=300)
plt.show()
print('Optimal cluster count K by Silhouette Coefficient: ', K_range[silhouette_list.index(max(silhouette_list))])
