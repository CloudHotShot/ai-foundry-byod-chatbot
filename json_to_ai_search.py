import json
import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex, SimpleField, SearchableField, SearchFieldDataType

"""
Set the following environment variables first:
- INPUT_FILE_PATH: Path to the JSON file containing book data
- AZURE_SEARCH_ADMIN_KEY: Your Azure Search service admin key
- AZURE_OPENAI_SEARCH_INDEX: Name of the Azure Search index to create or update
"""

### Remark:
## This script was tested on a books collection sample JSON File.

# Function to generate index schema from JSON data
def generate_index_schema(json_data):
    fields = []
    
    # Process the first book to get the schema structure
    if 'books' in json_data and len(json_data['books']) > 0:
        sample_book = json_data['books'][0]
        
        for key, value in sample_book.items():
            if isinstance(value, str):
                if key == "isbn":
                    # Make ISBN the key field and searchable
                    fields.append(SimpleField(name=key, type=SearchFieldDataType.String, key=True))
                else:
                    # Make other string fields searchable
                    fields.append(SearchableField(name=key, type=SearchFieldDataType.String))
            elif isinstance(value, int):
                fields.append(SimpleField(name=key, type=SearchFieldDataType.Int32))
            elif isinstance(value, float):
                fields.append(SimpleField(name=key, type=SearchFieldDataType.Double))
            elif isinstance(value, bool):
                fields.append(SimpleField(name=key, type=SearchFieldDataType.Boolean))
            else:
                # Default to searchable string for complex types
                fields.append(SearchableField(name=key, type=SearchFieldDataType.String))
    
    return fields

# Read JSON data from file
input_file = os.environ["INPUT_FILE_PATH"]
with open(input_file, 'r') as f:
    json_data = json.load(f)

# Generate the index schema
fields = generate_index_schema(json_data)

# Azure Search service details
service_name = "search-aihub"
admin_key = os.environ["AZURE_SEARCH_ADMIN_KEY"]

# Create a SearchIndexClient (not SearchIndexerClient)
endpoint = f"https://{service_name}.search.windows.net"
credential = AzureKeyCredential(admin_key)
index_client = SearchIndexClient(endpoint=endpoint, credential=credential)

# Define the index name
index_name = os.environ["AZURE_OPENAI_SEARCH_INDEX"]

try:
    # Try to get the existing index
    existing_index = index_client.get_index(index_name)
    print(f"Found existing index '{index_name}'. Updating with new fields...")
    
    # Update the existing index with new fields
    existing_index.fields.extend(fields)
    
    # Remove duplicate fields (in case some already exist)
    seen_fields = set()
    unique_fields = []
    for field in existing_index.fields:
        if field.name not in seen_fields:
            unique_fields.append(field)
            seen_fields.add(field.name)
    
    existing_index.fields = unique_fields
    
    # Update the index
    index_client.create_or_update_index(existing_index)
    print(f"Index '{index_name}' updated successfully with new fields.")
    
except Exception as e:
    if "not found" in str(e).lower():
        print(f"Index '{index_name}' not found. Creating new index...")
        
        # Create a new index if it doesn't exist
        new_index = SearchIndex(name=index_name, fields=fields)
        index_client.create_index(new_index)
        print(f"Index '{index_name}' created successfully.")
    else:
        print(f"Error: {e}")
        raise

# Display the fields that were added/updated
print("\nFields in the index:")
for field in fields:
    print(f"- {field.name} ({field.type}){' [KEY]' if getattr(field, 'key', False) else ''}")
