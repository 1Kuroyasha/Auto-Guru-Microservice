import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import category_encoders as ce
from sklearn.cluster import SpectralClustering
from controllers import get_collection


def get_cluster(car_id):
    collection = get_collection("clusters")
    cluster = collection.find_one({"carID": car_id})

    if cluster is None:
        distance_matrix = get_distance_matrix()

        model = SpectralClustering(
            random_state=0, n_clusters=2
        ).fit(distance_matrix)

        clusters = pd.DataFrame(
            data={"cluster": model.labels_}
        )

        clusters.index = distance_matrix.index

        cluster = int(clusters.loc[car_id, :].values[0])

        collection.insert_one({"carID": str(car_id), "cluster": cluster})
    else:
        cluster = int(cluster["cluster"])

    return cluster


def get_distance_matrix():
    collection = get_collection("cars")
    cars = collection.find({}, {"__v": 0, "sold": 0, "model": 0})

    labels = []
    data = {"make": [], "bodyType": [], "productionYear": [], "price": [],
            "engineCapacity": [], "transmission": [], "numberOfDoors": []}

    for car in cars:
        labels.append(str(car["_id"]))
        for key in data.keys():
            data[key].append(car[key])

    df = pd.DataFrame(data=data, index=labels)
    enc = ce.OneHotEncoder(cols=["make", "productionYear", "bodyType", "transmission", "engineCapacity", "numberOfDoors"],
                           return_df=True, handle_unknown="return_nan", handle_missing="return_nan", use_cat_names=True)
    encoded = enc.fit_transform(df)
    sim_matrix = pd.DataFrame(cosine_similarity(encoded))
    distance_matrix = pd.DataFrame(1-np.array(sim_matrix))
    distance_matrix.index = encoded.index
    distance_matrix.columns = encoded.index

    return distance_matrix
