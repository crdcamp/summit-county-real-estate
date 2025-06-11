import os
import json

def sort_layer_19_data():
    if os.path.exists('layer_19_data.json'):
        with open('layer_19_data.json', 'r') as f:
            data = json.load(f)
