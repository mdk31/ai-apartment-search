import json
import pytest
from unittest.mock import patch
from lambda_files.step_initate_lambda.handler import lambda_handler

# TODO: REFACTOR TO ABSOLUTE IMPORTS OF FUNCTIONS

@patch("handler.sfn_client.start_execution")
def test_lambda_handler_starts_step(mock_start):
    mock_start.return_value = {"executionArn": "arn:aws:states:...:execution-id"}

    event = {
        "body": json.dumps({'query': '2 bedroom apartment in manhattan'})
    }

    result = lambda_handler(event, None)
    assert result['statusCode'] == 200

    body = json.loads(result['body'])
    assert 'executionArn' in body
    mock_start.assert_called_once()