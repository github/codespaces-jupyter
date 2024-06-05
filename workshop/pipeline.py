import pandas as pd
from typing import Tuple
from datasets import load_dataset
import mlflow

from sentence_transformers import SentenceTransformer

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.neighbors import KNeighborsClassifier

from workshop.config import label_names

class Pipeline:
    def __init__(self):
        print("Initializing sentence transformers")
        self.embeddings_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        print("Setting correct mlflow tracking path")
        mlflow.set_tracking_uri("file:///workspaces/build-your-first-ml-pipeline-workshop/mlruns")

        self._mlflow_model = None

    def train(self, train_data = None, test_data = None, train_embeddings = None, sample_train_n=None):
        if not isinstance(train_data, pd.DataFrame) or not isinstance(test_data, pd.DataFrame):
            train_data, test_data = self.load_dataset()

        # to be able to test the pipeline faster we sample it down
        if sample_train_n:
            print(f"Sampling the training set to a smaller quantity {sample_train_n} ")
            train_data = train_data.sample(sample_train_n)

        if not isinstance(train_embeddings, pd.DataFrame):
            train_embeddings = self.create_embeddings(train_data)

        X_train, X_val, y_train, y_val = train_test_split(
            train_embeddings, train_data['label_name'], test_size=0.2, random_state=0)

        print("Training KNN")
        # TODO:  use mlflow to log this part, look at how to use autolog in mlflow documentation  
        knn = KNeighborsClassifier(n_neighbors=5, weights='distance', metric='cosine')
        knn.fit(X_train, y_train)
        y_pred = knn.predict(X_val)
        print(classification_report(y_val, y_pred))

        self.model = knn
        self.predict("I still haven't recieved my card, when will it be ready?")

        return self.model

    def load_dataset(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        dataset =  load_dataset("PolyAI/banking77", revision="main") # taking the data from the main branch
    
        train_data = pd.DataFrame(dataset['train'])
        test_data = pd.DataFrame(dataset['test'])

        train_data["label_name"] = train_data["label"].apply(lambda x: label_names[x])
        test_data["label_name"] = test_data["label"].apply(lambda x: label_names[x])

        return train_data, test_data
    
    def create_embeddings(self, train_data):
        print("Encoding embeddings")
        
        train_text_lists = train_data.text.tolist()

        train_embeddings = self.embeddings_model.encode(train_text_lists, show_progress_bar=True)

        return train_embeddings
    
    
    def predict(self, text_input: str):
        print(f"Prediction for {text_input}")
        if not self.model:
            raise Exception("You first need to train a model use pipeline.train to do so")
        
        print(self.model.predict(self.embeddings_model.encode(text_input).reshape(1, -1)))


    def predict_mlflow_model(self, text_input: str):
        if not self._mlflow_model:
            model_id = """REPLACE WITH YOUR ID"""
            self._mlflow_model = mlflow.sklearn.load_model(f"file:///workspaces/build-your-first-ml-pipeline-workshop/mlruns/0/{model_id}/artifacts/model")

        return self._mlflow_model.predict(self.embeddings_model.encode(text_input).reshape(1, -1))



if __name__ == "__main__":
    import fire
    fire.Fire(Pipeline)
