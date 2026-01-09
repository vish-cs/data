# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import functions_framework
from google.cloud import bigquery
import logging
from flask import jsonify
import os

# Initialize BigQuery Client
try:
    bq_client = bigquery.Client()
except Exception as e:
    logging.warning(f"Failed to initialize BigQuery client: {e}")
    bq_client = None

BQ_DATASET_ID = os.environ.get('BQ_DATASET_ID')
SPANNER_PROJECT_ID = os.environ.get('SPANNER_PROJECT_ID')
SPANNER_INSTANCE_ID = os.environ.get('SPANNER_INSTANCE_ID')
SPANNER_DATABASE_ID = os.environ.get('SPANNER_DATABASE_ID')
GCS_BUCKET_ID = os.environ.get('GCS_BUCKET_ID')


@functions_framework.http
def aggregation_helper(request):
    """
    HTTP Cloud Function that takes importName and runs a BQ query.
    """
    if not bq_client:
        return ('BigQuery client not initialized', 500)

    request_json = request.get_json(silent=True)
    if not request_json:
        return ('Request is not a valid JSON', 400)

    import_list = request_json.get('importList')
    if not import_list:
        return ("'importList' parameter is missing", 400)

    logging.info(f"Received request for importList: {import_list}")

    results = []

    try:
        for import_item in import_list:
            import_name = import_item.get('importName')
            if not import_name:
                logging.warning(
                    f"Skipping item without importName: {import_item}")
                continue

            query = None
            # Define specific queries based on importName
            if "india_census" in import_name:
                # Placeholder for India Census specific logic
                query = """
                    SELECT @import_name as import_name, CURRENT_TIMESTAMP() as execution_time
                 """
            elif "us_census" in import_name:
                # Placeholder for US Census specific logic
                query = """
                    SELECT @import_name as import_name, CURRENT_TIMESTAMP() as execution_time
                 """
            else:
                logging.info(
                    f"No specific aggregation logic for import: {import_name}")
                continue

            if query:
                job_config = bigquery.QueryJobConfig(query_parameters=[
                    bigquery.ScalarQueryParameter("import_name", "STRING",
                                                  import_name),
                ])
                query_job = bq_client.query(query, job_config=job_config)
                query_results = query_job.result()
                for row in query_results:
                    results.append(dict(row))

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logging.error(f"Aggregation failed: {e}")
        return (f"Aggregation failed: {str(e)}", 500)
