import boto3
import os

ecs = boto3.client('ecs')
logs = boto3.client('logs')
sns = boto3.client('sns')

sns_topic_arn = os.environ["SNS_TOPIC_ARN"]


def get_task_definition(task_definition_arn):
    response = ecs.describe_task_definition(taskDefinition=task_definition_arn)
    return response['taskDefinition']


def get_most_recent_log_stream(log_group, log_stream_prefix):
    most_recent_stream = None
    paginator = logs.get_paginator('describe_log_streams')
    for page in paginator.paginate(logGroupName=log_group, logStreamNamePrefix=log_stream_prefix):
        sorted_streams = sorted(page['logStreams'], key=lambda x: x['lastIngestionTime'], reverse=True)
        for stream in sorted_streams:
            if stream['logStreamName'].startswith(log_stream_prefix):
                most_recent_stream = stream
                break
        if most_recent_stream:
            break
    return most_recent_stream


def get_logs(log_group, log_stream_name):
    if log_stream_name:
        response = logs.get_log_events(logGroupName=log_group, logStreamName=log_stream_name, limit=20,
                                       startFromHead=False)
        return response['events']
    return []


def lambda_handler(event, context):
    detail = event.get('detail', {})
    containers = detail.get('containers', [])
    task_definition_arn = detail.get('taskDefinitionArn')

    for container in containers:
        exit_code = container.get('exitCode')
        if exit_code != 0:
            task_definition = get_task_definition(task_definition_arn)
            log_configuration = task_definition['containerDefinitions'][0]['logConfiguration']
            log_group = log_configuration['options']['awslogs-group']
            log_stream_prefix = log_configuration['options']['awslogs-stream-prefix']

            most_recent_stream = get_most_recent_log_stream(log_group, log_stream_prefix)
            log_stream_name = most_recent_stream['logStreamName'] if most_recent_stream else None
            cloudwatch_logs = get_logs(log_group, log_stream_name)
            log_messages = [log['message'] for log in cloudwatch_logs]

            error_message = (f"Task failed with exit code {exit_code}.\n\n"
                             f"Log Group: {log_group}\n"
                             f"Log Stream: {log_stream_name}\n\n"
                             f"Last 20 log entries:\n" + "\n".join(log_messages))
            sns.publish(TopicArn=sns_topic_arn, Message=error_message, Subject='ECS Task Failure Alert')
            break

    return {'message': 'Execution completed'}
