import json

import boto3
import requests

my_lambda = boto3.client('lambda')

TELEGRAM_BOT_TOKEN = "5755885376:AAFugbFmfwPKfHWTdNlhX6brhKyvYsbrwSA"

REPORTS = {
    "sweden00001": {
        "plantid": {
            "name": "Plant report",
            "lambda_function": "dev_sw_sweden00001_plantid_report",
            "duration": "5min"
        },
        "marketing_harvesting": {
            "name": "Marketing harvest prediction report",
            "lambda_function": "dev_sw_sweden00001_marketing_harvesting_report_daily",
            "duration": "3min"
        },
        "container_events": {
            "name": "Container events report",
            "lambda_function": "dev_sw_sweden00001_container_events_report_daily",
            "duration": "3min"
        },
        "seedling_report": {
            "name": "Seedling report",
            "lambda_function": "dev_sw_sweden00001_seedling_report",
            "duration": "3min"
        },
        "panel_summary": {
            "name": "Panels report",
            "lambda_function": "dev_sw_sweden00001_panel_summary_report_daily",
            "duration": "3min"
        },
        "sales_report": {
            "name": "Sales report",
            "lambda_function": "dev_sw_sweden00001_sales_report",
            "duration": "4min"
        },
        "harvesting": {
            "name": "Harvest prediction report",
            "lambda_function": "dev_sw_sweden00001_harvesting_report_daily",
            "duration": "3min"
        },
    }
}


def lambda_handler(event, context):
    try:
        main(event)
    except Exception as e:
        print("Something bad happened, I don't know what")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


def send_message(body):
    res = requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json=body)
    print(res.json())


def strategy(body):
    if "callback_query" in body:
        return handle_response(body["callback_query"])
    if "message" in body:
        return handle_start(body["message"])
    print("You should not reach here...")


def handle_response(callback_query):
    data = callback_query["data"]
    message = callback_query["message"]
    factory = message["chat"]["title"].lower()
    selection = REPORTS[factory][data]
    body = {
        "chat_id": message["chat"]["id"],
        "parse_mode": "Markdown",
        "text": f'Ok, {selection["name"]} will be ready in {selection["duration"]}.',
    }
    send_message(body)
    try:
        res = my_lambda.invoke(
            FunctionName=selection["lambda_function"],
            InvocationType='Event',
            Payload=json.dumps({
                "time_override": True
            }).encode()
        )
    except Exception as e:
        fallback_body = {
            "chat_id": message["chat"]["id"],
            "parse_mode": "Markdown",
            "text": f'I couldn\'t trigger the report... sorry',
        }
        send_message(fallback_body)


def handle_start(message):
    if "text" not in message:
        print("Nothing for me to do here")
        return
    full_command = message["text"]
    command, *rest = full_command.split(" ")
    command, *mention = command.split("@")
    if command != "/report":
        body = {
            "chat_id": message["chat"]["id"],
            "parse_mode": "Markdown",
            "text": f'I don\'t know what you mean... Try /report'
        }
        return send_message(body)

    if not rest:
        return handle_reports_options(message)

    if rest:
        report_name = rest[0]
        factory = message["chat"]["title"].lower()
        try:
            selection = REPORTS[factory][report_name]
        except Exception as e:
            body = {
                "chat_id": message["chat"]["id"],
                "parse_mode": "Markdown",
                "text": f'This report is not available...'
            }
            send_message(body)
            return handle_reports_options(message)

        body = {
            "chat_id": message["chat"]["id"],
            "parse_mode": "Markdown",
            "text": f'Ok, {selection["name"]} will be ready in {selection["duration"]}.',
        }
        send_message(body)
        try:
            my_lambda.invoke(
                FunctionName=selection["lambda_function"],
                InvocationType='Event',
                Payload=""
            )
        except Exception as e:
            fallback_body = {
                "chat_id": message["chat"]["id"],
                "parse_mode": "Markdown",
                "text": f'I couldn\'t trigger the report... sorry',
            }
            send_message(fallback_body)


def handle_reports_options(message):
    chat_id = message["chat"]["id"]
    factory = message["chat"]["title"].lower()
    contextual_reports = REPORTS[factory]
    body = {
        "chat_id": chat_id,
        "parse_mode": "Markdown",
        # "reply_to_message_id": message["message_id"],
        "text": f"Here's the list of available reports:",
        "reply_markup": json.dumps(
            {"inline_keyboard":
                 [[{"text": contextual_reports[r]["name"], "callback_data": r}] for r in REPORTS[factory].keys()]
             }
        )
    }
    send_message(body)


def main(event):
    print(event)
    body = json.loads(event["body"])
    strategy(body)


if __name__ == '__main__':
    with open("event.json", "r") as f:
        main(json.load(f))
