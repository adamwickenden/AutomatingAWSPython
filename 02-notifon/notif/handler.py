import os
import requests

slack_webhook_url = os.environ['SLACK_WEBHOOK_URL']

def post_to_slack_launch(event, context):    

    #format.(**event) => glob(**) operator takes the event as a dictionary and allows it to be passed into the string
    slack_message = "From {source} at {detail[StartTime]}: {detail[Description]}".format(**event)

    data = {"text":slack_message}
    requests.post(slack_webhook_url, json=data)

    return

def post_to_slack_terminate(event, context):

    #format.(**event) => glob(**) operator takes the event as a dictionary and allows it to be passed into the string
    slack_message = "From {source} at {detail[StartTime]}: {detail[Description]}".format(**event)

    data = {"text":slack_message}
    requests.post(slack_webhook_url, json=data)

    return
