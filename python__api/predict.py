import tensorflow as tf
import numpy as np
from PIL import Image
from models import SessionLocal, ImagePrediction

class PlantPredictor:
    def __init__(self, plant_model, disease_model, growth_stage_model):
        self.plant_name_model = plant_model
        self.disease_model = disease_model
        self.growth_stage_model = growth_stage_model

        self.plant_names = ["Bananas", "Tomatoes"]
        self.disease_labels = ["Late Blight", "Early Blight"]
        self.growth_stage_labels = ["Flowering", "Fruiting", "Vegetative"]

    def predict(self, image_path):
        # Preprocess the image
        image = Image.open(image_path)
        image = image.resize((224, 224))
        image = np.array(image) / 255.0
        image = image.reshape(1, 224, 224, 3)  # Reshape for model input

        # Make predictions with each model
        plant_name_prediction = self.plant_name_model.predict(image)
        disease_prediction = self.disease_model.predict(image)
        growth_stage_prediction = self.growth_stage_model.predict(image)

        return plant_name_prediction, disease_prediction, growth_stage_prediction

def predict_and_store_predictions(image_id, image_path):
    # Load the Plant Name model, Disease model, and Growth Stage model (replace these paths with your actual model paths)
    plant_name_model = tf.keras.models.load_model('plant_name_model.h5')
    disease_model = tf.keras.models.load_model('disease_model.h5')
    growth_stage_model = tf.keras.models.load_model('growth_stage_model.h5')

    # Initialize the PlantPredictor class with the loaded models
    plant_predictor = PlantPredictor(plant_name_model, disease_model, growth_stage_model)

    # Use the PlantPredictor instance to make predictions
    plant_name_prediction, disease_prediction, growth_stage_prediction = plant_predictor.predict(image_path)

    # Extract the predicted class indices
    predicted_plant_index = np.argmax(plant_name_prediction[0])
    predicted_disease_index = np.argmax(disease_prediction[0])
    predicted_growth_stage_index = np.argmax(growth_stage_prediction[0])

    # Map the indices to class labels
    predicted_plant_name = plant_predictor.plant_names[predicted_plant_index]
    predicted_disease = plant_predictor.disease_labels[predicted_disease_index]
    predicted_growth_stage = plant_predictor.growth_stage_labels[predicted_growth_stage_index]

    db = SessionLocal()

    # Create an ImagePrediction record and associate it with the captured image
    image_prediction = ImagePrediction(
        plant_name=predicted_plant_name,
        disease=predicted_disease,
        growth_stage=predicted_growth_stage,
        captured_image_id=image_id
    )
    
    db.add(image_prediction)
    db.commit()
    db.close()
