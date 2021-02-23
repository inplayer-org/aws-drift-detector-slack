import requests
import json
import urllib.parse
import os


def get_emoji_for_status(status):
    if status == 'DELETED':
        return ':x:'
    elif status == 'MODIFIED':
        return ':warning:'
    elif status == 'IN_SYNC':
        return ':heavy_check_mark:'

    return ''


def get_stack_url(stack_id):
    return f'https://console.aws.amazon.com/cloudformation/home#/stacks/drifts?stackId={urllib.parse.quote(stack_id)}'


def build_slack_message(stack):
    stack_url = get_stack_url(stack['StackId'])
    stack_name = stack['StackName']

    show_in_sync_resources = os.environ.get('SHOW_IN_SYNC', 'false')

    blocks = []
    if stack['no_of_drifted_resources'] > 0:
        blocks = create_drifted_stack_message_blocks(show_in_sync_resources, stack, stack_name, stack_url)

    elif show_in_sync_resources == 'true':
        blocks = create_not_drifted_stack_message_blocks(stack_name, stack_url)

    return {
        'blocks': blocks
    }


def create_not_drifted_stack_message_blocks(stack_name, stack_url):
    return [{
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': ':heavy_check_mark: No drift detected at *<'
                    + stack_url + '|' + stack_name
                    + '>*'
        }
    }]


def create_drifted_stack_message_blocks(show_in_sync_resources, stack, stack_name, stack_url):
    blocks = [{
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': ':warning: Drift detected at *<'
                    + stack_url + '|' + stack_name
                    + '>*'
        }
    }, {
        'type': 'divider',
    }]

    for drift in stack['drift']:
        if show_in_sync_resources == "false" and drift['StackResourceDriftStatus'] == 'IN_SYNC':
            continue

        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ">" + get_emoji_for_status(drift['StackResourceDriftStatus'])
                        + " *" + drift['PhysicalResourceId'] + "*\n>:small_orange_diamond: _"
                        + drift['ResourceType'] + "_"
            },
        })
    blocks.append({
        'type': 'divider',
    })

    return blocks


def build_detection_failed_slack_message(detection_failed_stack):
    stack_url = get_stack_url(detection_failed_stack['StackId'])
    stack_name = detection_failed_stack['StackName']

    return {'blocks': [{
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': ':question: Detection failed at *<'
                    + stack_url + '|' + stack_name
                    + '>*'
        }
    }]}


def post_to_slack(event):
    url = os.environ['SLACK_WEBHOOK']
    stacks = event.get("stacks")
    detection_failed_stacks = event.get("detection_failed_stacks")

    headers = {
        "Content-Type": "application/json"
    }

    for detection_failed_stack in detection_failed_stacks:
        message = build_detection_failed_slack_message(detection_failed_stack)
        requests.post(url, headers=headers, data=json.dumps(message))

    for stack in stacks:
        message = build_slack_message(stack)
        requests.post(url, headers=headers, data=json.dumps(message))


def lambda_handler(event, context):
    try:
        print("Slack notification lambda")

        post_to_slack(event)
    except Exception as e:
        print("Unexpected error: %s" % e)
        raise

    return {
        "statusCode": 200,
        "body": '',
    }