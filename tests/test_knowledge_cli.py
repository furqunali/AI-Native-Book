from knowledge_cli import build_parser

def test_cli_defaults_to_validation_root():
    args=build_parser().parse_args([])
    assert str(args.root)=="."
    assert args.validate is False

def test_cli_accepts_export_paths():
    args=build_parser().parse_args(["--jsonl","chunks.jsonl","--manifest","manifest.json","--validate"])
    assert str(args.jsonl)=="chunks.jsonl"
    assert str(args.manifest)=="manifest.json"
    assert args.validate is True
