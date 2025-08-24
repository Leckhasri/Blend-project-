import gradio as gr
import joblib
import numpy as np

# Load your trained model
model = joblib.load("fuel_blend_model.pkl")

# Define prediction function
def predict(feature1, feature2, feature3, feature4, feature5):
    X = np.array([[feature1, feature2, feature3, feature4, feature5]])
    return model.predict(X)[0]

# Create Gradio interface
iface = gr.Interface(
    fn=predict,
    inputs=["number", "number", "number","number","number"],  # match number of features
    outputs="number"
)

# Launch web UI
iface.launch()
