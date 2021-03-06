'''
Assign weigths to multiple models
Select all models to predict values
'''

import h2o
import numpy as np
import math
from dataprocessor import ProcessData
from h2o.estimators import H2ODeepLearningEstimator
from sklearn.metrics import mean_squared_error, mean_absolute_error

# config
_nmodels = 10
_lim = 2

# initialize server
h2o.init()

# get processed data
pTrain = ProcessData.trainData(moving_k_closest_average=True, standard_deviation=True)
pTest = ProcessData.testData(moving_threshold_average=True, standard_deviation=True)

# convert to h2o frames
hTrain = h2o.H2OFrame(pTrain)
hTest = h2o.H2OFrame(pTest)
hTrain.set_names(list(pTrain.columns))
hTest.set_names(list(pTest.columns))

# select column names
response_column = 'RUL'

training_columns = list(pTrain.columns)
training_columns.remove(response_column)
training_columns.remove("UnitNumber")
training_columns.remove("Time")

# split frames
train, validate = hTrain.split_frame([0.8])
test = hTest
ground_truth = np.array(pTest['RUL'])

# Building model
model_arr = range(_nmodels)

print "Building models"
print "---------------"
for i in range(_nmodels):
    model_arr[i] = H2ODeepLearningEstimator(hidden=[200, 200], score_each_iteration=True, variable_importances=True)
print "Build model complete...\n"

print "Train models"
print "------------"
for i in range(_nmodels):
    print "Train : " + str(i + 1) + "/" + str(_nmodels)
    model_arr[i].train(x=training_columns, y=response_column, training_frame=h2o.rbind(train, validate))
print "Train model complete...\n"

print "Predicting"
print "----------"
predicted_arr = range(_nmodels)
for i in range(_nmodels):
    predicted_arr[i] = model_arr[i].predict(test)
print "Prediction complete...\n"

print "Filter Predictions"
print "------------------"
predicted_vals = np.zeros(shape=100)
for i in range(len(test[:,0])):
    tmp = []
    for j in range(_nmodels):
        tmp.append(predicted_arr[j][i, 0])

    predicted_vals[i] = (sum(tmp[_lim:-_lim]) / float(len(tmp[_lim:-_lim])))
print "Filter predictions complete...\n"

print "Result"
print "------"

print "Root Mean Squared Error :", math.sqrt(mean_squared_error(ground_truth, predicted_vals))
print "Mean Absolute Error     :", mean_absolute_error(ground_truth, predicted_vals)








