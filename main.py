from api import API
from config import get_response_format
import json
import os

def main():
    response_format = get_response_format()
    api = API()
    response = api.safe_completion(messages=[{"role": "user", "content": "Prepare flashcards for the following topic: Web-scraping"}], response_format=response_format)
    print(json.dumps(response.json(), indent=4))

if __name__ == "__main__":
    main()
   