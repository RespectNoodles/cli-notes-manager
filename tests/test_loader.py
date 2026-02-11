from notes_cli.content.loader import pretty_name

def test_pretty_name():
    assert pretty_name("sql-injection") == "Sql Injection"
    assert pretty_name("john_the_ripper") == "John The Ripper"
