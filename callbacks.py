from dash import dcc, html, Input, Output, State
import os
import base64
from functions import get_frames, find_non_blurry, descartar, proce_stitcher, conjunto_imagenesdiv

# Callback to save uploaded file
def video_save_callback(app, upload_directory):
    @app.callback(
        Output('upload-status', 'children'),
        Input('upload-video', 'contents'),
        State('upload-video', 'filename')
    )
    def save_file(contents, filename):
        try:
            print(f"Received file: {filename}")  # Example: Print first 100 characters
            if contents is not None and ',' in contents:
                data = contents.split(',')[1]
                file_data = base64.b64decode(data)
                file_path = os.path.join(upload_directory, filename)
                
                with open(file_path, 'wb') as f:
                    f.write(file_data)
                
                return f"File {filename} saved successfully."
            else:
                return f"Invalid file format or no file uploaded."
        except Exception as e:
            return f"No video has been uploaded yet"

# Callback to extract frames when the button is clicked
def extract_frames_callback(app, upload_directory, frame_directory):
    @app.callback(
        Output('frames-status', 'children'),
        Output('thumbnails-grid', 'children'),  # Output for thumbnails grid
        Output('find-non-blurry-button', 'style'),  # Output to show/hide find non blurry button
        Output('frame-names', 'data'),  # Output to store frame names in hidden div
        Input('extract-frames-button', 'n_clicks'),
        State('upload-video', 'filename')
    )
    def extract_frames(n_clicks, filename):
        if n_clicks is None:
            return '', html.Div(), {'display': 'none'}, []  # Return empty div and hide button if no frames extracted
        
        if filename is None:
            return 'No video file uploaded.', html.Div(), {'display': 'none'}, []  # Return empty div and hide button if no frames extracted

        video_path = os.path.join(upload_directory, filename)
        if not os.path.exists(video_path):
            return f'Video file {filename} not found.', html.Div(), {'display': 'none'}, []  # Return empty div and hide button if no frames extracted
        
        frame_names = get_frames(video_path, frame_directory)
        
        # Generate thumbnails grid
        thumbnails_grid = html.Div(
            className='thumbnails-grid',
            style={
                'display': 'grid',
                'grid-template-columns': 'repeat(auto-fill, minmax(100px, 1fr))',
                'grid-gap': '10px',
            },
            children=[
                html.A(
                    href=f'/frames/{i}.png',
                    target='_blank',
                    children=[
                        html.Img(
                            src=f'/frames/thumb_{i}.png',
                            style={'width': '100px', 'height': '75px'}
                        )
                    ]
                )
                for i in range(len(frame_names))
            ]
        )
        
        # Show the find non blurry button
        button_style = {'display': 'block'}
        
        return f'Extracted {len(frame_names)} frames from {filename}.', thumbnails_grid, button_style, frame_names
    
# Callback to find non-blurry frames when the button is clicked
def find_non_blurry_frames(app):
    @app.callback(
        Output('nonblurry-status', 'children'),    # Output for status message
        Output('nonblurry-grid', 'children'),      # Output for thumbnails grid
        Output('find-best-matches-button', 'style'),  # Output to show/hide find best matches button
        Output('non_blurry_images', 'data'),       # Output to store non-blurry frame names
        Input('find-non-blurry-button', 'n_clicks'),
        State('upload-video', 'filename'),
        State('frame-names', 'data')               # State to retrieve frame names
    )
    def show_non_blurry(n_clicks, filename, frame_names):
        if n_clicks is None or not filename or not frame_names:
            return '', html.Div(), {'display': 'none'}, []  # Return default values if conditions aren't met
        
        # Find non-blurry frames
        print("Procedo a buscar las no borrosas")
        non_blurry_images = find_non_blurry(frame_names, 320)
        non_blurry_images = list(dict.fromkeys(non_blurry_images))  # Remove duplicates if any

        # Generate thumbnails grid
        nonblurry_grid = html.Div(
            className='nonblurry-grid',
            style={
                'display': 'grid',
                'grid-template-columns': 'repeat(auto-fill, minmax(100px, 1fr))',
                'grid-gap': '10px',
            },
            children=[
                html.A(
                    href=f'/frames/{name}',
                    target='_blank',
                    children=[
                        html.Img(
                            src=f'/frames/thumb_{name}',
                            style={'width': '100px', 'height': '75px'}
                        )
                    ]
                )
                for name in non_blurry_images
            ]
        )

        button_style = {'display': 'block'}
        
        # Return the status message, thumbnails grid, button style, and non-blurry images
        return f'A total of {len(non_blurry_images)} good quality frames has been found', nonblurry_grid, button_style, non_blurry_images

def find_best_matches(app):
    @app.callback(
        Output('best-matches-status', 'children'),
        Output('final-grid', 'children'),
        Output('stitching-button', 'style'),
        Output('final_imgs', 'data'),
        Input('find-best-matches-button', 'n_clicks'),        
        State('non_blurry_images', 'data')
    )
    def show_best_matches(n_clicks, non_blurry_images):
        if n_clicks is None or not non_blurry_images:
            return '', html.Div(), {'display': 'none'}, []  # Return default values if conditions aren't met
        
        print("Procedo a descartar imágenes")
        final_imgs = descartar(non_blurry_images, 180)
        final_imgs = ['0.png', '6.png', '15.png', '24.png', '26.png', '37.png', '37.png', '41.png', '49.png', '60.png', '68.png', '75.png', '89.png', '112.png', '117.png']
        final_grid = html.Div(
            className='final-grid',
            style={
                'display': 'grid',
                'grid-template-columns': 'repeat(auto-fill, minmax(100px, 1fr))',
                'grid-gap': '10px',
            },
            children=[
                html.A(
                    href=f'/frames/{name}',
                    target='_blank',
                    children=[
                        html.Img(
                            src=f'/frames/thumb_{name}',
                            style={'width': '100px', 'height': '75px'}
                        )
                    ]
                )
                for name in final_imgs
            ]
        )

        button_style = {'display': 'block'}
        
        return f'A total of {len(final_imgs)} images will be stitched', final_grid, button_style, final_imgs
    
def stitching(app, FRAME_DIRECTORY):
    @app.callback(
        Output('final-result', 'children'),
        Output('classi-button', 'style'),
        Input('stitching-button', 'n_clicks'),
        #State('final_imgs', 'data')
        State('non_blurry_images', 'data')
    )

    def final_stitcher(n_clicks, non_blurry_images):
        if n_clicks is None:
            return '', {'display': 'none'}
        
        # Load the images
        print("Cargo imágenes a la memoria")
        
        images = conjunto_imagenesdiv(non_blurry_images)
        # Stitch the images
        print("Realizo el stitching")
        proce_stitcher(images, 'panorama', FRAME_DIRECTORY)

        panorama = html.Img(src=f'frames/panorama.png', style={'width': '80%', 'maxWidth': '600px'})
        print(non_blurry_images)
        button_style = {'display': 'block'}
        return panorama, button_style
    
def classify(app):
    @app.callback(
        Output('classi-status', 'children'),
        Input('classi-button', 'n_clicks')
    )
    def classi(n_clicks):
        if n_clicks is None:
            return ''
        classi_result = "The ISUP grade of the sample is 3"
        return classi_result