import os
import csv
import logging
from datetime import datetime
from io import StringIO
from typing import Union, List, Dict
import re
import requests

from arcgis.gis import GIS
from arcgis.features import FeatureLayer
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError


class SurveyDataInterface:
    """
    A class to interface with ArcGIS to fetch survey data, convert it to CSV, and upload it to Google Cloud Storage.

    Attributes:
        base_url (str): Base URL for the feature layers.
        csv_names (List[str]): List of CSV file names to be used when uploading to GCS.
        bucket_name (str): Name of the Google Cloud Storage bucket where files will be uploaded.
        gis_client (GIS): ArcGIS GIS client for interacting with ArcGIS Online.
        storage_client (storage.Client): Google Cloud Storage client for interacting with GCS.
    """

    def __init__(self, base_url: str, csv_names: List[str], bucket_name: str) -> None:
        """
        Initializes the SurveyDataInterface with the base URL, CSV names, and bucket name.

        Parameters:
            base_url (str): The base URL for the feature layers.
            csv_names (List[str]): List of names for the CSV files.
            bucket_name (str): The GCS bucket name where the CSV files will be uploaded.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.csv_names = csv_names
        self.bucket_name = bucket_name
        try:
            self.base_url = self._validate_and_format_url(base_url)
        except Exception as e:
            self.logger.info(f"Error with base_url format: {e}")
            raise
        try:
            self.gis_client = self._connect_to_gis()
        except Exception as e:
            self.logger.info(f"Failed to initialize gis clients: {e}")
            raise
        try:
            self.storage_client = storage.Client()
        except Exception as e:
            self.logger.info(f"Failed to initialize gcs clients: {e}")
            raise
        self.final_file_names = {}

    @staticmethod
    def _validate_and_format_url(url: str) -> str:
        """Method to validate url used to fetch survey data

        This method takes the feature layer url and ensures it is correctly formatted. The formatting check
        isn't very strict since we're not 100% sure how a "proper" feature layer url should be. This method
        just checks the overall format.

        In particular, it makes sure that the url has a trailing forward slash. The method will add a 
        trailing forward slash to the url if there is none in the given input base_url

        Parameters: 
            url (str): base_url as specified in the config file

        Returns:
            (str): formatted & validated url to use to fetch feature layer data
        """
        if not url.endswith('/'):
            url += '/'
        pattern = r'^https://services\d+\.arcgis\.com/[A-Za-z0-9_\-]+/arcgis/rest/services/service_[a-f0-9]+/FeatureServer/$'

        if re.match(pattern, url):
            return url
        else:
            raise ValueError("URL does not match the expected format.")

    def _connect_to_gis(self) -> GIS:
        """
        Connects to ArcGIS Online using credentials from environment variables.

        Returns:
            GIS: An authenticated GIS client instance.
        """
        self.logger.info("Connecting to ArcGIS...")
        try:
            s123_username = os.environ.get("s123_username")
            s123_password = os.environ.get("s123_password")

            if not s123_username or not s123_password:
                raise ValueError(
                    "Environment variables for credentials not set properly."
                )

            with open(s123_username, "r") as file:
                s123_username = file.read().strip()
            with open(s123_password, "r") as file:
                s123_password = file.read().strip()

            return GIS(username=s123_username, password=s123_password)
        except Exception as e:
            self.logger.info(f"Error connecting to ArcGIS: {e}")
            raise

    def _get_feature_layer(self, i: int) -> FeatureLayer:
        """
        Constructs the feature layer URL and returns a FeatureLayer object for it.

        Parameters:
            i (int): The index to append to the base URL to form the full feature layer URL.

        Returns:
            FeatureLayer: The FeatureLayer object for the given URL.
        """
        try:
            feature_layer_url = self.base_url + str(i)
            return FeatureLayer(feature_layer_url, self.gis_client)
        except Exception as e:
            self.logger.info(f"Failed to get feature layer: {e}")
            raise

    def get_survey_data(self, feature_layer: FeatureLayer) -> List[Dict]:
        """
        Fetches survey data from a given feature layer and returns it as a list of dictionaries.

        Parameters:
            feature_layer (FeatureLayer): The feature layer from which to fetch survey data.

        Returns:
            List[Dict]: A list of dictionaries, each representing a survey response.
        """
        try:
            feature_layer_dict = self._get_survey_data_from_feature_layer(
                feature_layer)
            return self._parse_feature_layer_data(feature_layer_dict)
        except Exception as e:
            self.logger.info(f"Error getting survey data: {e}")
            return []

    def _get_survey_data_from_feature_layer(self, feature_layer: FeatureLayer) -> List[Dict]:
        """
        Queries the given feature layer for all records and returns the features as a list of dictionaries.

        Parameters:
            feature_layer (FeatureLayer): The feature layer to query.

        Returns:
            List[Dict]: The "features" part of the query response, as a list of dictionaries.
        """
        try:
            fl_response = feature_layer.query(return_all_records=True)
            fl_dict = fl_response.to_dict()
            return fl_dict.get("features")
        except Exception as e:  # Catching a broad exception due to import resolution issue
            self.logger.info(f"Error querying feature layer: {e}")
            raise

    def _parse_feature_layer_data(self, feature_layer_data: List[Dict]) -> List[Dict]:
        """
        Parses the raw feature layer data into a list of dictionaries representing survey responses.

        Parameters:
            feature_layer_data (List[Dict]): Raw feature layer data to parse.

        Returns:
            List[Dict]: Parsed survey responses.
        """
        try:
            survey_responses = []
            for response in feature_layer_data:
                survey_responses.append(response.get("attributes"))
            return survey_responses
        except Exception as e:
            self.logger.info(f"Error parsing feature layer data: {e}")
            return []

    def convert_dict_to_csv(self, data: List[Dict]) -> str:
        """
        Converts a list of dictionaries to a CSV string.

        Parameters:
            data (List[Dict]): The data to convert to CSV format.

        Returns:
            str: The CSV data as a string.
        """
        try:
            csv_output = StringIO()
            csv_writer = csv.DictWriter(csv_output, fieldnames=data[0].keys())
            csv_writer.writeheader()
            csv_writer.writerows(data)
            return csv_output.getvalue()
        except Exception as e:
            self.logger.info(f"Error converting data to CSV: {e}")
            return ""

    def upload_to_gcs(self, data: str, dest_file_name: str) -> None:
        """
        Uploads the given data string as a CSV file to Google Cloud Storage.

        Parameters:
            data (str): The CSV data to upload.
            dest_file_name (str): The destination file name in GCS.
        """
        try:
            if not data:
                self.logger.info("No data to upload.")
                return
            bucket_client = self.storage_client.bucket(self.bucket_name)
            blob = bucket_client.blob(dest_file_name)
            blob.upload_from_string(data, content_type='text/csv')
            self.logger.info(
                f"File {dest_file_name} uploaded to {self.bucket_name}.")
        except GoogleCloudError as e:
            self.logger.info(f"Error uploading to GCS: {e}")
        except Exception as e:
            self.logger.info(
                f"An unexpected error occurred while uploading to GCS: {e}")

    @staticmethod
    def datestamp_fname(fname: str) -> str:
        fname_split = fname.split('.')
        today_date = datetime.today().strftime("%Y%m%d")
        return f'{fname_split[0]}_fall2023_{today_date}.{fname_split[-1]}'

    def get_survey_data_to_gcs(self) -> None:
        """
        Fetches survey data for each feature layer, converts it to CSV, and uploads it to GCS.
        """
        for i, fname in enumerate(self.csv_names):
            if fname == 'advocacy_survey.csv':
                fname = self.datestamp_fname(fname)
                self.final_file_names['advocacy_survey_file'] = fname
            feature_layer = self._get_feature_layer(i)
            survey_responses = self.get_survey_data(feature_layer)
            if not survey_responses:
                self.logger.info(
                    f"No responses found for feature layer {i}. Skipping upload.")
                continue
            survey_data_csv = self.convert_dict_to_csv(survey_responses)
            if not survey_data_csv:
                self.logger.info(
                    f"CSV conversion failed for feature layer {i}. Skipping upload.")
                continue
            self.upload_to_gcs(survey_data_csv, fname)

    def read_api_endpoint(self) -> Union[str, None]:
        """
        Reads the API endpoint URL from an environment variable. The environment variable
        is the path of where the secret containing the API endpoint URL is stored as a volume.
        If the environment variable is not set, logs an informational message and returns None. 
        If the file cannot be opened or read for any reason, logs an error message and returns None.

        Returns:
            str: The API endpoint URL if the file is found and readable.
            None: If the environment variable is not set or file cannot be accessed.
        """
        ppln_endpoint_path = os.environ.get(
            "advo_survey_ppln_endpoint", "not_found")
        if ppln_endpoint_path == "not_found":
            self.logger.info("bad path to mage ppln api endpoint")
            return None
        try:
            with open(ppln_endpoint_path, "r") as file:
                ppln_endpoint = file.read().strip()
            return ppln_endpoint
        except IOError as e:
            self.logger.error(
                f"Failed to read the API endpoint file at {ppln_endpoint_path}: {e}")
            return None

    def trigger_advoacy_mage_ppln(self) -> Union[Dict, None]:
        """
        Triggers the advocacy pipeline by making a POST request to the API endpoint
        with a specified JSON payload. It includes environment variables and file paths
        necessary for the pipeline run.

        Returns:
            Dict: The response from the API if the request was successful.
            None: If the API endpoint is not set or the request failed.
        """
        api_endpoint = self.read_api_endpoint()
        if api_endpoint is None:
            self.logger.error("API endpoint is not available.")
            return None
        file_name = self.final_file_names.get('advocacy_survey_file').replace('csv', 'parquet')
        object_key = f'fall_2023/{file_name}'
        self.logger.info(f"Object key passed to mage runtime vars: {object_key}")
        payload = {
            "pipeline_run": {
                "variables": {
                    "layer_env": "prod",
                    "object_key": object_key,
                    "path_to_keyfile": "../../secrets/bigquery/bigquery_key_prod"
                }
            }
        }
        try:
            response = requests.post(api_endpoint, json=payload)
            response.raise_for_status()
            self.logger.info(response.json())
            return response.json()  
        except requests.exceptions.HTTPError as http_err:
            self.logger.error(f"HTTP error occurred: {http_err}")
        except Exception as err:
            self.logger.error(f"An error occurred: {err}")

        return None

def dummy():
    return "hey dummy"


if __name__ == "__main__":
    import toml
    with open('./config.toml', 'r') as f:
        config = toml.load(f)
    base_url = config.get("arcgis_config").get("base_url")
    csv_names = config.get("arcgis_config").get("csv_names_in_destination")
    bucket_name = config.get("gcp_config").get("bucket_name")
    megatron = SurveyDataInterface(base_url, csv_names, bucket_name)
    megatron.get_survey_data_to_gcs()