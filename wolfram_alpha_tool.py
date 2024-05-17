import wolframalpha
import logging
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app_id = os.getenv('APP_ID')

# Set up Wolfram Alpha API authentication
client = wolframalpha.Client(app_id)

# Set up logging
logging.basicConfig(filename='logs/wolfram_alpha_tool.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def wolfram_alpha_tool(query, format='default', include_fields=None, exclude_fields=None, **kwargs):
    """
    Custom CrewAI tool to interface with the Wolfram Alpha API.

    Args:
        query (str): The natural language query to be sent to Wolfram Alpha.
        format (str, optional): The desired format for the response. Defaults to 'default'.
        include_fields (list, optional): A list of fields to include in the response. Defaults to None.
        exclude_fields (list, optional): A list of fields to exclude from the response. Defaults to None.
        **kwargs: Additional parameters to pass to the Wolfram Alpha API.

    Returns:
        str: The formatted response containing the relevant information from Wolfram Alpha.
    """
    try:
        # Send the query to Wolfram Alpha API and get the response
        res = client.query(query, **kwargs)
        answer = next(res.results).text

        # Check if the result is paginated
        if hasattr(res, 'more_from'):
            # Fetch additional pages if needed
            additional_results = fetch_additional_pages(res.more_from, **kwargs)
            res.results.extend(additional_results)

        # Extract relevant fields from the JSON response
        input_query = res.query
        result = format_result(res.results, format, include_fields, exclude_fields)

        # Format the response
        response = f"Input Query: {input_query}\n\nResult: {result}"

        return response

    except wolframalpha.exceptions.WolframAlphaException as e:
        # Handle errors from the API
        error_message = str(e)
        logging.error(f"WolframAlphaException: {error_message}")
        return f"Error: {error_message}"

    except Exception as e:
        # Handle any other exceptions
        error_message = str(e)
        logging.error(f"General Exception: {error_message}")
        return f"Error: {error_message}"


def format_result(results, format_type, include_fields=None, exclude_fields=None):
    """
    Format the Wolfram Alpha API results based on the specified format and field filters.

    Args:
        results (list): The list of Wolfram Alpha API result objects.
        format_type (str): The desired format for the result (e.g., 'default', 'html', 'plaintext').
        include_fields (list, optional): A list of fields to include in the result. Defaults to None.
        exclude_fields (list, optional): A list of fields to exclude from the result. Defaults to None.

    Returns:
        str: The formatted result string.
    """
    formatted_results = []
    for result in results:
        if format_type == 'default':
            formatted_result = result.text
        elif format_type == 'html':
            formatted_result = result.html
        elif format_type == 'plaintext':
            formatted_result = result.plaintext
        else:
            formatted_result = result.text

        if include_fields:
            formatted_result = '\n'.join([getattr(result, field) for field in include_fields if hasattr(result, field)])
        elif exclude_fields:
            excluded_fields = [getattr(result, field) for field in exclude_fields if hasattr(result, field)]
            formatted_result = formatted_result.replace('\n'.join(excluded_fields), '')

        formatted_results.append(formatted_result)

    return '\n\n'.join(formatted_results)


def fetch_additional_pages(more_from_url, **kwargs):
    """
    Fetch additional result pages from the Wolfram Alpha API.

    Args:
        more_from_url (str): The URL to fetch additional result pages from.
        **kwargs: Additional parameters to pass to the API request.

    Returns:
        list: A list of additional Wolfram Alpha API result objects.
    """
    additional_results = []
    while more_from_url:
        response = requests.get(more_from_url, **kwargs)
        response.raise_for_status()
        additional_data = response.json()
        additional_results.extend(additional_data['results'])
        more_from_url = additional_data.get('more_from', None)

    return additional_results
