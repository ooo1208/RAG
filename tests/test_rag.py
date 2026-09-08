import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rag_lab import KnowledgeBase, answer, demo


class RetrievalTests(unittest.TestCase):
    def test_live_response_requires_text_and_real_citation(self):
        hit = {'id': 'known', 'source': 'policy.md', 'page': 1, 'first_line': 1, 'last_line': 1, 'body': '采购主管审批'}
        for content in ['[]', '{"answer":"","citations":["known"]}', '{"answer":"内容","citations":["fake"]}']:
            with self.subTest(content=content), patch.dict('os.environ', {'MODEL_BASE_URL': 'https://example.invalid/v1', 'MODEL_API_KEY': 'test', 'MODEL_NAME': 'test'}):
                with patch('rag_lab.request_json', return_value={'choices': [{'message': {'content': content}}]}):
                    with self.assertRaises(ValueError):
                        answer('谁审批', [hit], live=True)
        with patch.dict('os.environ', {'MODEL_BASE_URL': 'https://example.invalid/v1', 'MODEL_API_KEY': 'test', 'MODEL_NAME': 'test'}):
            with patch('rag_lab.request_json', return_value={'choices': []}):
                with self.assertRaises(ValueError):
                    answer('谁审批', [hit], live=True)

    def test_demo_sources_are_correct(self):
        result = demo()
        self.assertEqual(result['top1_cases_passed'], result['total_cases'])

    def test_isolation_update_and_citation_locations(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'policy.md'
            source.write_text('内部说明\n采购主管负责审批\n', encoding='utf-8')
            with KnowledgeBase(Path(folder) / 'kb.sqlite') as kb:
                kb.ingest('alice', source)
                self.assertEqual(kb.retrieve('bob', '采购主管'), [])
                old = kb.retrieve('alice', '采购主管')[0]
                self.assertEqual(old['first_line'], 1)
                self.assertEqual(old['last_line'], 2)
                source.write_text('新版本\n合同归档由法务负责\n', encoding='utf-8')
                kb.ingest('alice', source)
                self.assertEqual(kb.retrieve('alice', '采购主管'), [])
                current = kb.retrieve('alice', '合同归档')[0]
                self.assertNotEqual(old['id'], current['id'])
                self.assertIn('法务', answer('谁归档', [current])['citations'][0]['text'])

    def test_empty_and_unsupported_input_keep_original_index(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'policy.md'
            source.write_text('采购主管负责审批', encoding='utf-8')
            with KnowledgeBase(Path(folder) / 'kb.sqlite') as kb:
                kb.ingest('alice', source)
                source.write_text('', encoding='utf-8')
                with self.assertRaises(ValueError):
                    kb.ingest('alice', source)
                self.assertTrue(kb.retrieve('alice', '采购主管'))
                self.assertEqual(answer('星际飞船', [])['mode'], 'no_evidence')

    def test_vectors_are_required_and_invalidated_after_update(self):
        class FakeEmbeddings:
            model, base = 'test-only', 'local-test'
            def encode(self, texts):
                return [[1.0, 0.0] for _ in texts]
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'policy.md'
            source.write_text('采购主管负责审批', encoding='utf-8')
            with KnowledgeBase(Path(folder) / 'kb.sqlite') as kb:
                kb.ingest('alice', source)
                with self.assertRaises(ValueError):
                    kb.retrieve('alice', '采购', embedding=FakeEmbeddings())
                kb.build_vectors('alice', FakeEmbeddings())
                self.assertTrue(kb.retrieve('alice', '采购', embedding=FakeEmbeddings()))
                kb.ingest('alice', source)
                with self.assertRaises(ValueError):
                    kb.retrieve('alice', '采购', embedding=FakeEmbeddings())


if __name__ == '__main__':
    unittest.main()
