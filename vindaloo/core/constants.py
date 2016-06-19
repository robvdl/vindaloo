# A map for translating the ?format= query parameter value to a mimetype.
# More can be added later, but for now we can only handle json and html.
MIMETYPES = {
    'json': 'application/json',
    'html': 'text/html',
    'xhtml': 'application/xhtml+xml',
    'pdf': 'application/pdf',
    'csv': 'text/csv',
    'xml': 'application/xml'
}
