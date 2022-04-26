# from main import *

import os
import time
import base64

import webbrowser
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from video import yolo_final

# Repertoires pour stockées les vidéos et les résultats de vidéos
UPLOAD_DIRECTORY = "upload_files"
ASSETS_DIRECTORY = "assets"

# Création du répertoire s'il n'existe pas
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# Création d'une application Dash
app = dash.Dash(__name__)

# Création du layout
# Contient une Div principale, une zone d'upload et des 2 boutons pour valider son choix
app.layout = html.Div(
    children=[
        html.H1(children="Détection d'objets dans une vidéo",
                className="header_title"),

        html.Br(),  # Retour à la ligne

        html.Div(children=[
            dcc.Upload(id="upload_data", className="upload_line",
                       children=[
                           html.P(children=["Drag and Drop or ",
                                            html.A('Select a File', id="link")
                                            ], className="texte", id="message"),

                       ]),
        ], style={"text-align": "center"}, hidden=False, id="div_upload"),

        html.Br(),
        html.Div([
            html.Button(children=
                        html.P(children="Appliquer Yolo", className="texte_button"),
                        id='button', n_clicks=0, hidden=False
                        ),
            html.A(html.Button(children=
                               html.P(children="Tester avec nouvelle vidéo", className="texte_button"),
                               id="button_refresh"), href='/'),
        ], style={"text-align": "center"}),

        html.Br(),
        html.Div(id='article', children=[
            html.Video(id="output-data", className="toVideo", controls=True, hidden=True)
        ], style={"text-align": "center", "font-size": "150%", "color": "#FFFFFF"})

    ], style={"background-color": "#FFFFFF"}
)


# Pour encoder la vidéo récemment reçu et la stockée dans le dossier upload_files
def save_file(name, content):
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


# 1ère callback, appelée lorsqu'on envoie notre vidéo au serveur --> appel de change_line(...)
@app.callback(
    [Output("message", "children"),
     Output("upload_data", "className"),
     Output('button', 'n_clicks'),
     Output("output-data", "hidden")],
    [Input("upload_data", "contents"),
     State("upload_data", "filename")]
)
def change_line(contents, filename):
    # Si un vidéo a bien été recu, on la sauvegarde
    if contents and filename:
        print("Fichier recu par le serveur")
        save_file(filename, contents)
        return [filename], "upload_line_middle", 0, True
    else:
        return dash.no_update


# 2nde callback appelé lorsqu'on clique sur appliquer Yolo, si le clic est effectif, on lance Yolo sur la vidéo
@app.callback(
    [Output("output-data", "src"),
     Output("output-data", "hidden"),
     Output("div_upload", "hidden"),
     Output("button", "hidden")],
    [Input('button', 'n_clicks'),
     Input("upload_data", "contents"),
     State("upload_data", "filename")]
)
def run_script_onClick(n_clicks, list_of_content, filename):
    """
        Callback appelée lors qu'on clique sur appliquer Yolo
    Parameters
    ----------
    n_clicks
    list_of_content
    filename

    Returns
    -------
    la vidéo
    montre la div où est affichée la vidéo
    cache la div d'upload
    cache le bouton d'appliquer Yolo

    """
    if not n_clicks:
        return dash.no_update

    if list_of_content is not None:
        result = os.path.join(ASSETS_DIRECTORY, "result_" + filename)
        # Si un résultat du même nom existe, on la supprime
        if os.path.exists(result):
            os.remove(result)
        print("Passage dans le yolo")
        yolo_final(os.path.join(UPLOAD_DIRECTORY, filename), result)
        print("La video est créée")

        return result, False, True, True


# Pour lancer le serveur
if __name__ == "__main__":
    webbrowser.open('http://127.0.0.1:8050/')
    app.title = "Detecter des objets dans une video"
    app.run_server(debug=False)
