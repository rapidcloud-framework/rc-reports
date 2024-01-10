#!/usr/bin/env python3

__author__ = "Igor Royzis"
__copyright__ = "Copyright 2023, Kinect Consulting"
__license__ = "Commercial"
__email__ = "iroyzis@kinect-consulting.com"

import logging
import json
import traceback
from boto3.dynamodb.conditions import Key

logger = logging.getLogger("server")
logger.setLevel(logging.INFO)


def example_data():
    return [
        {"name": "example"}
    ]


def report_document_mapping(boto3_session, user_session, params):
    try:
        env = params["env"]
        report_name = params["report_name"]
        dataset_name = params["dataset_name"]
        if report_name != "" and dataset_name != "":
            fqn = f"{env}_report_{report_name}_{dataset_name}"
            resp = boto3_session.resource('dynamodb').Table("metadata").query(
                KeyConditionExpression=Key('profile').eq(env) & Key('fqn').eq(fqn)
            )['Items']
            print(resp)
            if len(resp) > 0:
                mappings = json.loads(resp[0]["params"]["report_mappings"].replace("\\",""))
                logger.info(json.dumps(mappings, indent=2, default=str))
                return mappings
            else:
                fqn = f"{env}_report_define_report_{report_name}"
                report_definition = boto3_session.resource('dynamodb').Table("metadata").query(
                    KeyConditionExpression=Key('profile').eq(env) & Key('fqn').eq(fqn)
                )['Items'][0]["params"]["report_definition"]
                # "report_mappings": "{\"from1\":\"to1\",\"from2\":\"to2\"}",
                report_mappings = {}
                for col in report_definition:
                    report_mappings[col["csv_col_name"]] = col["csv_col_name"]
                return report_mappings

    except Exception as e:
        logger.error(e)
        traceback.print_exc()

    return {}


def custom_endpoint(action, params, boto3_session, user_session):
    if action == "example":
        return example_data()
    elif action == "report_document_mapping":
        return report_document_mapping(boto3_session, user_session, params)
    else:
        logger.warning(f"no such endpoint: {action}")
        return []
