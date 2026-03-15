import os
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

# Config
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 15
LEARNING_RATE = 0.0001
DATA_PATH = "/Users/gparthasrikar/Documents/m-project/apps/api/data/dataset_b.csv"
MODEL_SAVE_PATH = "/Users/gparthasrikar/Documents/m-project/apps/api/models/model_b.h5"

def load_data():
    df = pd.read_csv(DATA_PATH)
    train_df = df[df['split'] == 'train']
    val_df = df[df['split'] == 'val']
    
    train_df['label'] = train_df['label'].astype(str)
    val_df['label'] = val_df['label'].astype(str)
    
    return train_df, val_df

def create_model():
    # Use ResNet50
    base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    
    for layer in base_model.layers:
        layer.trainable = False
        
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(1, activation='sigmoid')(x)  # Binary: 0=Ischemia, 1=Bleeding
    
    model = Model(inputs=base_model.input, outputs=predictions)
    
    model.compile(optimizer=Adam(learning_rate=LEARNING_RATE),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
    return model

def main():
    print("Loading data for Model B (Type Classification)...")
    train_df, val_df = load_data()
    print(f"Train size: {len(train_df)}, Val size: {len(val_df)}")
    
    datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True
    )
    
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    train_generator = datagen.flow_from_dataframe(
        dataframe=train_df,
        x_col="filepath",
        y_col="label",
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='binary',
        shuffle=True
    )
    
    val_generator = val_datagen.flow_from_dataframe(
        dataframe=val_df,
        x_col="filepath",
        y_col="label",
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='binary',
        shuffle=False
    )
    
    model = create_model()
    # model.summary()
    
    callbacks = [
        ModelCheckpoint(MODEL_SAVE_PATH, save_best_only=True, monitor='val_accuracy'),
        EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
    ]
    
    print("Starting Training Model B...")
    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=val_generator,
        callbacks=callbacks
    )
    
    print("Training Complete.")
    model.save(MODEL_SAVE_PATH)

if __name__ == "__main__":
    main()
