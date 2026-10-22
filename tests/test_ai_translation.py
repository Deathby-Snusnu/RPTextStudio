import io
import json
import unittest
from unittest.mock import patch
from ai_translation import inspect_translation, translate

class TranslationTests(unittest.TestCase):
    def test_tokens(self):
        self.assertEqual(inspect_translation("Hallo %s und %p", "Bonjour %p et %s"), [])
        self.assertTrue(inspect_translation("Hallo %s", "Hello"))
        self.assertTrue(inspect_translation("%% %p", "%p"))
        self.assertTrue(inspect_translation("Hallo", "Hello %q"))

    def test_emotes_and_newlines(self):
        self.assertEqual(inspect_translation("*winkt*", "*waves*"), [])
        self.assertTrue(inspect_translation("*winkt*", "waves"))
        self.assertTrue(inspect_translation("Hallo", "*Hello*"))
        self.assertTrue(inspect_translation("Hallo", "Hello\\nthere".replace("\\n","\n")))

    def test_api_is_explicit_and_not_stored(self):
        class Reply:
            def __enter__(self):
                return io.BytesIO(json.dumps({"output":[{"content":[
                    {"type":"output_text","text":"Hello %s"}]}]}).encode())
            def __exit__(self, *args):
                pass
        with patch("urllib.request.urlopen",return_value=Reply()) as openurl:
            result=translate("Hallo %s","enUS",api_key="unit-test-key",
                             model="gpt-5-mini",addon="HexerRP")
            self.assertEqual(result,"Hello %s")
            payload=json.loads(openurl.call_args.args[0].data)
            self.assertIs(payload["store"],False)
            self.assertEqual(payload["model"],"gpt-5-mini")
        with self.assertRaises(ValueError):
            translate("Test","frFR",api_key="",model="gpt-5-mini",addon="HexerRP")

if __name__ == "__main__":
    unittest.main()
