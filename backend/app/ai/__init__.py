"""Shelf Life Estimator — AI Layer Package."""



# In Colab — run this after training
!pip install tf2onnx

import tf2onnx
import tensorflow as tf

model = tf.keras.models.load_model("/content/drive/MyDrive/fresco_model.keras")

# Convert to ONNX
spec = (tf.TensorSpec(model.input_shape, tf.float32, name="input"),)
model_proto, _ = tf2onnx.convert.from_keras(model, input_signature=spec, output_path="/content/drive/MyDrive/fresco_model.onnx")
print("Saved fresco_model.onnx")
