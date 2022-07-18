import pandas as pd
import numpy as np
from bson.json_util import dumps
from bson.objectid import ObjectId
from scipy.spatial import distance
from controllers import get_collection
from services import get_cluster


def calculate_similarity_between_cars(a, b):
    total = 0

    # [make, bodyType, transmission, enginCapacity, productionYear, numberOfDoors, price]
    weights = [2, 2, 3, 3, 1, 1, 1]
    summation = sum(weights)

    for index, pair in enumerate(zip(a, b)):
        if type(pair[0]) is str:
            if pair[0] == pair[1]:
                total += weights[index]
        elif pair[0] == None or pair[1] == None:
            continue
        else:
            euclidean_distance = distance.euclidean(int(pair[0]), int(pair[1]))
            if euclidean_distance == 0:
                total += weights[index]
            else:
                total += weights[index]/euclidean_distance

    return total/summation


def calculate_similarity(user_preferences, car):
    total = 0

    weights = {
        "make": 2,
        "bodyType": 2,
        "transmission": 3,
        "engineCapacity": 3,
        "productionYear": 1,
        "numberOfDoors": 1,
        "price": 1
    }

    summation = 0

    for key, _ in user_preferences.items():
        summation += weights[key]

        if type(user_preferences[key]) is str:
            if user_preferences[key] == car[key]:
                total += weights[key]
        elif user_preferences[key] == None or car[key] == None:
            continue
        else:
            euclidean_distance = distance.euclidean(
                int(user_preferences[key]), int(car[key]))
            if euclidean_distance == 0:
                total += weights[key]
            else:
                total += weights[key]/euclidean_distance

    return total/summation


def retrieval():
    collection = get_collection("cars")
    cursor = collection.find(
        {}, {"_id": 1, "make": 1, "productionYear": 1, "price": 1, "bodyType": 1, "transmission": 1, "engineCapacity": 1, "numberOfDoors": 1})

    cars = []
    for car in cursor:
        cars.append(car)

    return cars


def recommend(user_id):
    collection = get_collection("preferences")
    user_preferences = collection.find_one({"userID": user_id}, {"filters": 1})
    user_preferences = user_preferences["filters"]

    if user_preferences is None:
        return "{}"

    print(user_preferences)

    cars = retrieval()

    labels = []

    for car in cars:
        labels.append(str(car["_id"]))

    df = pd.DataFrame(data=cars, index=labels)
    df = df.drop(axis=1, columns=["_id"])

    similarity_list = []
    for _, row in df.iterrows():
        similarity_list.append(calculate_similarity(user_preferences, row))

    df = pd.DataFrame(data={"similarity": similarity_list}, index=labels)
    df = df.sort_values("similarity", axis=0, ascending=False)

    if df.size < 6:
        return "{}"

    df = df.drop(index=np.array(df.index[6:]))

    return dumps(np.array(df.index))


def get_recommended_cars(car_id):
    cluster = get_cluster(car_id)
    cluster_collection = get_collection("clusters")
    car_collection = get_collection("cars")
    retrieved = cluster_collection.find({"cluster": cluster}, {"carID": 1})

    cars = []
    labels = []

    for car in retrieved:
        cars.append(car_collection.find_one({"_id": ObjectId(car["carID"])}, {
            "_id": 0, "make": 1, "productionYear": 1, "price": 1, "bodyType": 1, "transmission": 1, "engineCapacity": 1, "numberOfDoors": 1
        }))

        labels.append(car["carID"])

    df = pd.DataFrame(data=cars, index=labels)

    similarity_list = []
    for _, row in df.iterrows():
        similarity_list.append(
            calculate_similarity_between_cars(row, df.loc[car_id, :]))

    df = pd.DataFrame(data={"similarity": similarity_list}, index=labels)
    df = df.sort_values("similarity", axis=0, ascending=False)
    df = df.drop(index=car_id)

    if df.size < 6:
        return dumps(np.array(df.index))

    df = df.drop(index=np.array(df.index[6:]))

    return dumps(np.array(df.index))
