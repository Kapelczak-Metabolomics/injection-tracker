import streamlit as st
import requests
from requests.auth import HTTPBasicAuth

# Replace with your LabKey server details
LABKEY_SERVER = "https://your.labkey.server.com"
LABKEY_CONTAINER = "/your/labkey/container"
LABKEY_USERNAME = "your_username"
LABKEY_PASSWORD = "your_password"

# Query parameters (adapt as needed)
QUERY_NAME = "your_query_name" #Name of your LabKey query which already orders the metabolites
SCHEMA_NAME = "your_schema_name" #Name of the schema
SORT_COLUMN = "your_ranking_column" #Column used to sort metabolites (e.g., 'Abundance')


def get_labkey_data(params):
    """Retrieves top 50 metabolites from LabKey."""
    url = f"{LABKEY_SERVER}{LABKEY_CONTAINER}/query/executeQuery.api"
    auth = HTTPBasicAuth(LABKEY_USERNAME, LABKEY_PASSWORD)
    params.update({
        "query.queryName": QUERY_NAME,
        "schemaName": SCHEMA_NAME,
        "maxRows": 50, #Limit to top 50
        "query.sort": f"{SORT_COLUMN} DESC" #Sort in descending order, adjust if necessary
    })


    try:
        response = requests.get(url, auth=auth, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        if data and data['rows']:
            return data['rows']
        else:
            return None  # Indicate no data found
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to LabKey: {e}")
        return None
    except (KeyError, IndexError) as e:
        st.error(f"Error parsing LabKey response: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None


def main():
    st.title("Top 50 LabKey Metabolites")

    additional_params = {}  # Add any additional query parameters here

    metabolite_data = get_labkey_data(additional_params)

    if metabolite_data:
        st.write("Top 50 Metabolites:")
        st.dataframe(metabolite_data)  # Display data in a table
    else:
        st.info("No metabolite data found or error during retrieval.")


if __name__ == "__main__":
    main()
