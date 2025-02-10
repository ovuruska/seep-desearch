# Seep Desearch

Seep Desearch is a web search and report generation system that utilizes Google Custom Search API and LLMs (Large Language Models) to generate structured and insightful reports based on user queries.

## Installation

To get started, first clone the repository and install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the root directory with the following credentials:

```ini
BASE_URL=https://api.deepinfra.com/v1/openai
DEEPINFRA_API_KEY=<your_deepinfra_api_token>
GOOGLE_SEARCH_API_KEY=<your_google_search_api_key>
GOOGLE_SEARCH_CX=<your_google_search_cx>
```

### How to Obtain a DeepInfra API Key

1. **Create a DeepInfra Account:**  
   - Visit the [DeepInfra website](https://deepinfra.com/) and log in using your GitHub account.

2. **Generate an API Key:**  
   - Navigate to the [API Keys page](https://deepinfra.com/dash/api_keys).
   - Click on "New API Key."
   - Provide a name for your API key and click "Generate API Key."
   - Copy the generated API key for later use.

3. **Update the `.env` File:**  
   - Open the `.env` file in your project directory.
   - Locate the line starting with `DEEPINFRA_API_KEY=`.
   - Replace `<your_deepinfra_api_token>` with the API key you copied earlier:

   ```ini
   DEEPINFRA_API_KEY=your_actual_api_key_here
   ```

After completing these steps, your application will be configured to authenticate with DeepInfra using your API key.  
For more detailed information, refer to the [DeepInfra API Documentation](https://deepinfra.com/docs/deep_infra_api).

### How to use Google Custom Search:

1. Get your API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Create a Custom Search Engine and get your CX ID from [Google Programmable Search](https://programmablesearchengine.google.com/)
3. Add the credentials to your `.env` file:


## Running the Application

Once the dependencies are installed and the environment variables are set, you can run the application using Chainlit:

```bash
chainlit run app.py
```

This will start the Chainlit interface, where you can input queries and receive detailed reports generated using web search results and LLMs.

## Features

- **Automated Research Planning**: Extracts key topics from user queries.
- **Web Search Integration**: Uses Google Custom Search API to fetch relevant information.
- **Content Extraction**: Retrieves and processes webpage content for deeper insights.
- **Relevance Filtering**: Uses an LLM to filter and rank the most useful results.
- **Report Generation**: Creates structured Wikipedia-style reports in Markdown format.
- **Streaming Output**: Prevents UI freezing by streaming content gradually.

## Requirements

- Python 3.8+
- Google Custom Search API Key
- DeepInfra API Key
- Chainlit

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Feel free to submit pull requests or open issues to contribute to the project.

## Contact

For any inquiries or support, please reach out via email or open an issue in the repository.

