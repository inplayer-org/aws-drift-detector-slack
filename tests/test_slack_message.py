import os
import sys
import unittest

sys.path.insert(0, './drift_detector')

from drift_detector.slack_notification import build_slack_message

MOCK_STACK = {
    'StackId': 'mock_stack_id',
    'StackName': 'mock_stack_name',
    'drift': [
        {
            'PhysicalResourceId': 'mock_physical_resource_id_1',
            'ResourceType': 'AWS::S3::Bucket',
            'StackResourceDriftStatus': 'IN_SYNC'
        },
        {
            'PhysicalResourceId': 'mock_physical_resource_id_2',
            'ResourceType': 'AWS::ApiGateway::Method',
            'StackResourceDriftStatus': 'MODIFIED'
        },
        {
            'PhysicalResourceId': 'mock_physical_resource_id_3',
            'ResourceType': 'AWS::ApiGateway::RestApi',
            'StackResourceDriftStatus': 'DELETED'
        },
    ],
    'no_of_drifted_resources': 2,
    'no_of_resources': 3
}


class TestSlackMessageBuild(unittest.TestCase):
    def tearDown(self):
        # Reset 'SHOW_IN_SYNC_RESOURCES' back to default, after each test.
        os.environ['SHOW_IN_SYNC_RESOURCES'] = 'false'
        # Reset 'SHOW_IN_SYNC_STACKS' back to default, after each test.
        os.environ['SHOW_IN_SYNC_STACKS'] = 'false'

    def test_drift_message_generation(self):
        """
        Test that drift slack message is build correctly given stack data
        """
        mock_message = build_slack_message(MOCK_STACK)

        self.assertTrue(mock_message['blocks'])
        self.assertEqual(mock_message, {
            'blocks': [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":warning: Drift detected at *<https://console.aws.amazon.com/cloudformation/home#/stacks/drifts?stackId=mock_stack_id|mock_stack_name>*"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ">:warning: *mock_physical_resource_id_2*\n>:small_orange_diamond: _AWS::ApiGateway::Method_"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ">:x: *mock_physical_resource_id_3*\n>:small_orange_diamond: _AWS::ApiGateway::RestApi_"
                    }
                },
                {
                    "type": "divider"
                },
            ]
        })

    def test_drift_message_generation_with_show_in_sync_stacks_and_resources_enabled(self):
        """
        Test that drift slack message is build correctly given stack data
        """
        os.environ['SHOW_IN_SYNC_RESOURCES'] = 'true'
        os.environ['SHOW_IN_SYNC_STACKS'] = 'true'
        no_drift_mock_stack = MOCK_STACK.copy()
        no_drift_mock_stack['no_of_drifted_resources'] = 0

        mock_message = build_slack_message(no_drift_mock_stack)

        self.assertTrue(mock_message['blocks'])
        self.assertEqual(mock_message, {
            'blocks': [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":heavy_check_mark: No drift detected at *<https://console.aws.amazon.com/cloudformation/home#/stacks/drifts?stackId=mock_stack_id|mock_stack_name>*"
                    }
                },
            ]
        })

    def test_no_drift_message_generation_with_show_in_sync_stacks_and_resources_disabled(self):
        """
        Test that no drift slack message is build when show in sync is disabled
        """
        os.environ['SHOW_IN_SYNC_RESOURCES'] = 'false'
        os.environ['SHOW_IN_SYNC_STACKS'] = 'false'
        no_drift_mock_stack = MOCK_STACK.copy()
        no_drift_mock_stack['no_of_drifted_resources'] = 0

        mock_message = build_slack_message(no_drift_mock_stack)

        self.assertEqual(mock_message, {
            'blocks': []
        })

    def test_drift_message_generation_with_in_sync_resources(self):
        """
        Test that drift slack message is build correctly with in sync resources included
        """
        os.environ['SHOW_IN_SYNC_RESOURCES'] = 'true'

        mock_message = build_slack_message(MOCK_STACK)

        self.assertTrue(mock_message['blocks'])
        self.assertEqual(mock_message, {
            'blocks': [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":warning: Drift detected at *<https://console.aws.amazon.com/cloudformation/home#/stacks/drifts?stackId=mock_stack_id|mock_stack_name>*"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ">:heavy_check_mark: *mock_physical_resource_id_1*\n>:small_orange_diamond: _AWS::S3::Bucket_"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ">:warning: *mock_physical_resource_id_2*\n>:small_orange_diamond: _AWS::ApiGateway::Method_"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ">:x: *mock_physical_resource_id_3*\n>:small_orange_diamond: _AWS::ApiGateway::RestApi_"
                    }
                },
                {
                    "type": "divider"
                },
            ]
        })


if __name__ == '__main__':
    unittest.main()
