import asyncio
import aiohttp
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

async def fetch_data_from_api(session, url):
    """Fetch data from a single API asynchronously with error handling."""
    try:
        async with session.get(url, timeout=10) as response:
            response.raise_for_status()  # Raise an error for non-2xx responses
            return await response.json()  # Return JSON response
    except asyncio.TimeoutError:
        logging.error(f"Request to {url} timed out")
    except aiohttp.ClientResponseError as e:
        logging.error(f"Request to {url} failed with status {e.status}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
    return None  # Return None if an error occurs

async def fetch_concurrently(api_urls):
    """Fetch data from multiple APIs concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data_from_api(session, url) for url in api_urls]
        return await asyncio.gather(*tasks)  # Run all requests concurrently

def lambda_handler(event, context):
    """AWS Lambda handler function."""
    api_urls = event.get("api_urls", [])
    if not api_urls:
        return {"statusCode": 400, "body": json.dumps("No API URLs provided.")}

    results = asyncio.run(fetch_concurrently(api_urls))

    # Filter out None values (failed requests)
    return {"statusCode": 200, "body": json.dumps([res for res in results if res is not None])}

# Local testing
if __name__ == "__main__":
    event = {"api_urls": ["https://jsonplaceholder.typicode.com/todos/1", "https://jsonplaceholder.typicode.com/todos/2"]}
    response = lambda_handler(event, None)
    print("Response:", response)
