import dash_bootstrap_components as dbc
from dash import dcc, html

def create_layout():
    header = html.Div([
        html.Img(src='/assets/SiteImages/Logo.png', alt="HistoMerge", style={'height': '100px', 'width': 'auto'})
    ], style={'backgroundColor': 'grey', 'width': '100%', 'padding': '10px', 'boxSizing': 'border-box', 'textAlign': 'center'})

    thumbnails = html.Div([
        html.H1("Frames Section", style={'textAlign': 'center'}),
        html.Div(id='upload-status', style={'textAlign': 'center'}),        
        dcc.Upload(
            id='upload-video',
            children=html.Div(['Drag and Drop or ', html.A('Select a Video File')]),
            style={
                'width': '98%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            max_size=-1,
            multiple=False
        ),
        dbc.Button("Extract Frames", id="extract-frames-button", className="mb-3"),  
        html.Div(id='frames-status', style={'textAlign': 'center'}),      
        html.Div(id='thumbnails-grid', className='thumbnails-grid', style={'margin-bottom':'25px'}),  
        dbc.Button("Find non blurry frames", id="find-non-blurry-button", className="mb-3", style={'display': 'none'}),  # Initially hidden
        dcc.Store(id='frame-names', data=[]), 
        html.Div(id='nonblurry-status', style={'textAlign': 'center'}),       
        html.Div(id='nonblurry-grid', className='nonblurry-grid', style={'margin-bottom':'25px'}),        
        dbc.Button("Find best matches", id="find-best-matches-button", className="mb-3"),
        dcc.Store(id='non_blurry_images', data=[]),
        html.Div(id='best-matches-status', style={'textAlign': 'center'}),
        html.Div(id='final-grid', className='final-grid', style={'margin-bottom':'25px'}),
        dcc.Store(id='final_imgs', data=[]),
        html.Div(
            dbc.Button("Stitch", id="stitching-button", className="mb-3", style={'display': 'none'}),
            style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}
        ),
    ], style={'backgroundColor': '#A9A19F', 'overflowY': 'auto', 'flex': '1', 'maxHeight': 'calc(100vh - 120px)', 'border': '1px solid black', 'padding': '10px'})

    right_div = html.Div([
        html.Div(id="final-result", style={'textAlign': 'center', 'margin-bottom':'25px'}),
        html.Div(
            dbc.Button("Classify", id="classi-button", className="mb-3", style={'display': 'none'}),
            style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}
        ),
        html.Div(id='classi-status', style={'textAlign': 'center'}), 
    ], style={'backgroundColor': 'green', 'width': '50%', 'padding': '20px', 'boxSizing': 'border-box', 'overflowY': 'auto', 'maxHeight': 'calc(100vh - 120px)', 'border': '1px solid black'})

    content = html.Div([
        thumbnails,
        right_div
    ], style={'display': 'flex', 'flexDirection': 'row', 'height': '100%', 'width': '100%'})

    final_layout = html.Div([
        header,
        content
    ], style={'display': 'flex', 'flexDirection': 'column', 'height': '100vh', 'margin': '0', 'padding': '0', 'overflow': 'hidden'})

    return final_layout
