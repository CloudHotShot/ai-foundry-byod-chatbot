import os
os.environ["AZURE_OPENAI_ENDPOINT"] = os.environ["AZ_OPENAI_ENDPOINT"]

def chat_completion_oyd_studio_viewcode(question: str) -> str:
    import os
    from openai import AzureOpenAI
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    deployment = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]

    try:
        # Create credential and token provider - modern approach
        credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(
            credential, "https://cognitiveservices.azure.com/.default"
        )

        client = AzureOpenAI(
            azure_endpoint=endpoint,
            azure_ad_token_provider=token_provider,
            api_version="2024-12-01-preview"
        )

        completion = client.chat.completions.create(
            model=deployment,
            messages=[
                {
                    "role": "user",
                    "content": question,
                }
            ],
            extra_body={
                "data_sources": [
                    {
                        "type": "azure_search",
                        "parameters": {
                            "endpoint": os.environ["AZURE_OPENAI_SEARCH_ENDPOINT"],
                            "index_name": os.environ["AZURE_OPENAI_SEARCH_INDEX"],
                            "authentication": {"type": "system_assigned_managed_identity"},
                        },
                    }
                ]
            },
        )

        return completion.choices[0].message.content
        
    except Exception as e:
        # Enhanced error handling with fallback options
        error_msg = str(e)
        
        if "DefaultAzureCredential" in error_msg:
            return f"Authentication Error: Please ensure you're logged in with 'az login' or running on Azure with managed identity. Details: {error_msg}"
        elif "401" in error_msg or "Unauthorized" in error_msg:
            return f"Authorization Error: Please check your Azure OpenAI and AI Search permissions. Details: {error_msg}"
        elif "404" in error_msg or "Not Found" in error_msg:
            return f"Resource Error: Please verify your endpoint URLs and deployment names. Details: {error_msg}"
        else:
            return f"Unexpected Error: {error_msg}"