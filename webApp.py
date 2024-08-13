import dash
import dash_bootstrap_components as dbc
from flask import Flask
from layout import create_layout
from functions import create_paths
from callbacks import video_save_callback, extract_frames_callback, find_non_blurry_frames, find_best_matches, stitching, classify

# Initialize Flask server
# Initialize Flask server
server = Flask(__name__, static_url_path='/frames', static_folder='frames')

# Create the paths
UPLOAD_DIRECTORY, FRAME_DIRECTORY, RESULT_DIRECTORY = create_paths()
# Set maximum upload size to 1 GB (1,073,741,824 bytes)
server.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024
server.config['TIMEOUT'] = 600

# Initialize Dash app
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
# Create the layout. This is located in layout.py
app.layout = create_layout()

video_save_callback(app, UPLOAD_DIRECTORY)
extract_frames_callback(app, UPLOAD_DIRECTORY, FRAME_DIRECTORY)
find_non_blurry_frames(app)
find_best_matches(app)
stitching(app, FRAME_DIRECTORY)
classify(app)

# Run the server
if __name__ == '__main__':
    app.run_server(debug=False)
