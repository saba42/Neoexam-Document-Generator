import sys
import json
from document.doc_parser import parse_source_document

if len(sys.argv) > 1:
    filepath = sys.argv[1]
    result = parse_source_document(filepath)
    print(json.dumps(result, indent=2))
else:
    print("Please provide a filepath")
