"""Observe real Bedrock stream metadata without changing its text or transport."""
import json
import os
from pathlib import Path
import runpy

from fortune_teller.core.aws_connector import AWSBedrockConnector

original_initialize = AWSBedrockConnector._initialize_client


def initialize_with_observer(self):
    original_initialize(self)
    if self.client is None:
        return
    original_invoke = self.client.invoke_model_with_response_stream

    def invoke(**kwargs):
        response = original_invoke(**kwargs)
        body = response['body']

        def observe():
            try:
                for event in body:
                    if 'chunk' in event:
                        message = json.loads(event['chunk']['bytes'])
                        if message.get('type') in {'message_start', 'message_delta', 'message_stop'}:
                            # Only control metadata, never content blocks or credentials.
                            if message['type'] == 'message_start':
                                record = {'type': 'message_start',
                                          'model': message.get('message', {}).get('model'),
                                          'usage': message.get('message', {}).get('usage')}
                            else:
                                record = message
                            with Path(os.environ['E2E_BEDROCK_EVENTS']).open('a', encoding='utf-8') as log:
                                log.write(json.dumps(record) + '\n')
                    yield event
            finally:
                body.close()
        response['body'] = observe()
        return response

    self.client.invoke_model_with_response_stream = invoke


AWSBedrockConnector._initialize_client = initialize_with_observer
runpy.run_module('fortune_teller', run_name='__main__')
