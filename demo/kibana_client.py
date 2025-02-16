import base64
import requests

class KibanaClient:
    def __init__(self, **elk_credentials):
        """
        Initialize the Kibana client connector.
        :param host: Kibana host URL.
        :param user: Username for authentication.
        :param pass: Password for authentication.
        """
        self.host = elk_credentials['kibana_host']
        self.username = elk_credentials['user']
        self.password = elk_credentials['pass']
        self.timeout = 10

    def _get_auth_header(self):
        """Generate the Authorization header for Basic Auth."""
        auth_str = f"{self.username}:{self.password}"
        encoded_auth = base64.b64encode(auth_str.encode()).decode()
        return {"Authorization": f"Basic {encoded_auth}", "kbn-xsrf": "true"}

    def get_kibana_data(self):
        """Retrieve Kibana dashboards, spaces, and data views."""
        try:
            headers = self._get_auth_header()
    
            dashboards_url = f"{self.host}/api/saved_objects/_find?type=dashboard"
            dashboards_response = requests.get(dashboards_url, headers=headers, timeout=self.timeout)
            dashboards_response.raise_for_status()
            dashboards = len(dashboards_response.json().get("saved_objects", []))
            
            spaces_url = f"{self.host}/api/spaces/space"
            spaces_response = requests.get(spaces_url, headers=headers, timeout=self.timeout)
            spaces_response.raise_for_status()
            spaces = len(spaces_response.json())
            
            data_views_url = f"{self.host}/api/data_views"
            data_views_response = requests.get(data_views_url, headers=headers, timeout=self.timeout)
            data_views_response.raise_for_status()
            data_views = len(data_views_response.json().get("data_view", []))

            print(f"================================================================================")
            print(f"Kibana info")
            print(f"Number of dashboards: {dashboards}")
            print(f"Number of spaces: {spaces}")
            print(f"Number of data views: {data_views}")
            print(f"================================================================================")

            return {
                "dashboards": dashboards,
                "spaces": spaces,
                "dataViews": data_views,
            }
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving Kibana data: {str(e)}")
            return {"dashboards": 0, "spaces": 0, "dataViews": 0}
