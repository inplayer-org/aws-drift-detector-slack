# CloudFormation drift detector to Slack

## How it works

 1. CloudWatch triggers DiscoverStacks Lambda function.
 2. DiscoverStacks Lambda function gets stacks from CloudFormation.
 3. DiscoverStacks Lambda will split all of those stacks into smaller batches (for example 10 stacks per batch) and publish them to the SQS FIFO queue with the same MessageGroupID to prevent parallel invocations.
 4. DetectDrift Lambda function will be triggered by the FIFO queue and will perform actual drift detection on stacks.
 5. After drift detection, DetectDrift Lambda will invoke SendSlackNotification Lambda function asynchronously, and this Lambda will send an appropriate message to the Slack.

![diagram](https://github.com/patternmatch/aws-drift-detector-slack/blob/master/assets/drift-detector.png?raw=true)

## Parameters

 * SlackWebhook - Webhook URL for pushing messages to Slack.
 * Cron - How often drift detection should be run (eg. every twelve hours `0 0 */12 * ? *` more info [here](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html)).
 * ShowInSyncResources - Skip reporting of resources with no drift (reduces Slack message output).
 * StackRegex - Defines which stacks should be scanned for resource drift.
 * StackBatches - Number that indicates how many stacks should be send to SQS in one batch

More details can be found at https://driftdetector.com


## Local setup

Prerequisites:

 * Python3
 * Python virtualenv

Install dependencies by running:

```sh
pip install -r requirements.txt
```

## Testing

Executing unit tests:

```sh
make test
```