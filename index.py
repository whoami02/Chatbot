from flask import Flask, request, jsonify, render_template
import os
import dialogflow
import requests
import json
import pusher

# pusher_client = pusher.Pusher(
#     app_id=os.getenv('PUSHER_APP_ID'),
#     key=os.getenv('PUSHER_KEY'),
#     secret=os.getenv('PUSHER_SECRET'),
#     cluster=os.getenv('PUSHER_CLUSTER'),
#     ssl=True)

pusher_client = pusher.Pusher(
  app_id='934762',
  key='e50404c7b65a9e36babc',
  secret='bb5fbbfa657fe8102b7d',
  cluster='ap2',
  ssl=True
)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()

# @app.route('/get_crime_detail', methods=['POST'])
# def get_crime_detail():
#     data = request.get_json(silent=True)
#     crime = data['queryResult']['parameters']['movie']
#     api_key = os.getenv('OMDB_API_KEY')

#     crime_detail = requests.get('http://www.omdbapi.com/?t={0}&apikey={1}'.format(crime, api_key)).content
#     crime_detail = json.loads(crime_detail)
#     response = """ 
#         Title : {0}
#         Time : {1}
#         Place : {2}
#     """.format(crime_detail['Title'], crime_detail['Time'], crime_detail['Place'])
#     reply = {
#         "fulfillmentText" : response,
#     }

#     return jsonify(reply)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True)
    if data['queryResult']['queryText'] == 'Yes':
        reply = {
            "fulfillmentText": "Okay! Please proceed.",
        }
        return jsonify(reply)

    elif data['queryResult']['queryText'] == 'no':
        reply = {
            "fulfillmentText": "Goodbye!",
        }
        return jsonify(reply)

def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code = language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(
            session = session, query_input = query_input)
        
        return response.query_result.fulfillment_text

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    fulfillment_text = detect_intent_texts(project_id, "unique", message, 'en')
    response_text = { "message":  fulfillment_text }

    socketId = request.form['socketId']
    pusher_client.trigger('exp_bot', 'new_message', 
        {'human_message': message, 'bot_message': fulfillment_text},
    socketId)

    return jsonify(response_text)

