from explorer.html_analyzer import HtmlAnalyzer


def test_html_analyzer_extracts_page_information():
    html = """
    <html>
      <head><title>Example Site</title></head>
      <body>
        <h1>Welcome</h1>
        <p>This is an example website.</p>
        <a href="contact.html">Contact</a>
      </body>
    </html>
    """

    result = HtmlAnalyzer().analyze(html)

    assert result["title"] == "Example Site"
    assert result["heading"] == "Welcome"
    assert "contact.html" in result["links"]
    assert "example website" in result["summary"]
