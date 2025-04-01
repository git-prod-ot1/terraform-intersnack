import boto3
import datetime
import os
import pytz

ecs = boto3.client('ecs')

CLUSTER = None
TASK_DEFINITION = None
SUBNETS = None
SECURITY_GROUPS = None
NOTEBOOK_NAME = None

TEAMS_WEBHOOK_URL = None
TEAMS_ACTIVITY_TITLE = None
TEAMS_ACTIVITY_SUBTITLE = None
TEAMS_ACTIVITY_IMAGE = None

LAILO_WEBHOOK_URL = None
LAILO_ACTIVITY_TITLE = None

TELEGRAM_CHAT_ID = None
TELEGRAM_BOT_TOKEN = None
TELEGRAM_ACTIVITY_TITLE = None

ACTIVITY_TITLE = None

FACTORY = None
REPORT_EXT = None


def lambda_handler(event, context):
    init_env()
    time_override = event.get('time_override') or False
    if not time_override and should_skip():
        print("Incorrect time, skipping execution")
        return
    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    factory = os.environ.get('FACTORY') or ''

    response = ecs.run_task(
        cluster=CLUSTER,
        taskDefinition=TASK_DEFINITION,
        count=1,
        launchType='FARGATE',
        networkConfiguration={
            'awsvpcConfiguration': {
                'assignPublicIp': 'ENABLED',
                'subnets': SUBNETS,
                'securityGroups': SECURITY_GROUPS
            }
        },
        overrides={
            'containerOverrides': [
                {
                    'name': 'runner',
                    'environment': [
                                       {
                                           'name': 'FACTORY',
                                           'value': factory
                                       },
                                       {
                                           'name': 'NOTEBOOK_NAME',
                                           'value': NOTEBOOK_NAME
                                       },
                                       {
                                           'name': 'PROCESS_START',
                                           'value': now
                                       }
                                   ] + report_config(now) + parse_additional_vars()
                }
            ]
        }
    )


def init_env():
    global CLUSTER, TASK_DEFINITION, SUBNETS, SECURITY_GROUPS, NOTEBOOK_NAME

    CLUSTER = os.environ['CLUSTER']
    TASK_DEFINITION = os.environ['TASK_DEFINITION']
    SUBNETS = os.environ['SUBNETS'].split(',')
    SECURITY_GROUPS = os.environ['SECURITY_GROUPS'].split(',')
    NOTEBOOK_NAME = os.environ['NOTEBOOK_NAME']


def should_skip():
    target_time_str = os.environ.get("TARGET_LOCAL_TIME")
    if not target_time_str:
        return False

    target_tz = os.environ.get("TARGET_TZ") or "Europe/Berlin"
    zone = pytz.timezone(target_tz)
    local_time = datetime.datetime.strptime(target_time_str, "%H:%M")
    # local_time defaults here to 1900 which had different timezone offsets! Pytz can figure out day-to-day offsets
    # but we need to use the same day for it to work
    expected_naive = datetime.datetime.utcnow().replace(hour=local_time.hour, minute=local_time.minute)
    expected_localised = zone.localize(expected_naive)
    expected_utc = expected_localised.astimezone(pytz.UTC)
    now_utc = datetime.datetime.utcnow()

    return expected_utc.hour != now_utc.hour


def report_config(now):
    if os.environ.get('IS_REPORT') == "true":
        activity_title = os.environ.get('ACTIVITY_TITLE') or ''
        report_ext = os.environ.get('REPORT_EXT') or "pdf"
        factory = os.environ.get('FACTORY') or ''

        return [
            {
                'name': 'REPORT_NAME',
                'value': f"{NOTEBOOK_NAME}/{factory}_{NOTEBOOK_NAME}_{now}.{report_ext}"
            },
            {
                'name': 'REPORT_EXT',
                'value': report_ext
            },
            {
                'name': 'ACTIVITY_TITLE',
                'value': activity_title
            },
            {
                'name': 'TEAMS_WEBHOOK_URL',
                'value': os.environ.get('TEAMS_WEBHOOK_URL') or ''
            },
            {
                'name': 'TEAMS_ACTIVITY_TITLE',
                'value': os.environ.get('TEAMS_ACTIVITY_TITLE') or activity_title or ''
            },
            {
                'name': 'TEAMS_ACTIVITY_SUBTITLE',
                'value': os.environ.get('TEAMS_ACTIVITY_SUBTITLE') or ''
            },
            {
                'name': 'TEAMS_ACTIVITY_IMAGE',
                'value': os.environ.get('TEAMS_ACTIVITY_IMAGE') or ''
            },
            {
                'name': 'LAILO_WEBHOOK_URL',
                'value': os.environ.get('LAILO_WEBHOOK_URL') or ''
            },
            {
                'name': 'LAILO_ACTIVITY_TITLE',
                'value': os.environ.get('LAILO_ACTIVITY_TITLE') or activity_title or ''
            },
            {
                'name': 'TELEGRAM_BOT_TOKEN',
                'value': os.environ.get('TELEGRAM_BOT_TOKEN') or ''
            },
            {
                'name': 'TELEGRAM_CHAT_ID',
                'value': os.environ.get('TELEGRAM_CHAT_ID') or ''
            },
            {
                'name': 'TELEGRAM_ACTIVITY_TITLE',
                'value': os.environ.get('TELEGRAM_ACTIVITY_TITLE') or activity_title or ''
            },
        ]
    return []


def parse_additional_vars():
    report_vars = [v for v in os.environ if v.startswith('REPORTVAR_')]
    return [
        {'name': v.replace('REPORTVAR_', ''), 'value': os.environ[v]} for v in report_vars
    ]
