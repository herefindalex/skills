"""Each assertion pins a local packaging contract, not model behavior."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest
from support import make_package, approve, edit_manifest, SKILL
try:
    from tools.check_package import validate_package
except ModuleNotFoundError:
    validate_package = None


class PackageContractTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(callable(validate_package), 'validate_package is not implemented')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = make_package(Path(self.tmp.name) / 'package')

    def codes(self, **kwargs):
        return {x['code'] for x in validate_package(self.root, mode='draft', **kwargs)}

    def append(self, text):
        with (self.root / SKILL).open('a', encoding='utf-8') as f:
            f.write(text)

    def test_minimal_portable_manifest(self):
        self.assertEqual(validate_package(self.root, mode='draft'), [])

    def test_broken_reference(self):
        self.append('\n[missing](references/missing.md)\n')
        self.assertIn('MISSING_REFERENCE', self.codes())

    def test_valid_local_reference_and_fragment(self):
        p=self.root/'skills/investigate-company-role/references/evidence.md'
        p.parent.mkdir(); p.write_text('# Evidence\n', encoding='utf-8')
        self.append('\n[Evidence](references/evidence.md#evidence)\n')
        self.assertEqual(self.codes(), set())

    def test_reference_definition_checked(self):
        self.append('\nRead [source][ref].\n[ref]: references/not-here.md\n')
        self.assertIn('MISSING_REFERENCE', self.codes())

    def test_external_url_and_example_in_fence_not_read(self):
        self.append('\n[Docs](https://developers.openai.com/plugins/build/skills)\n'
                    '```md\n[Example](missing-example.md)\n```\n')
        self.assertEqual(self.codes(), set())

    def test_reject_app_mcp_and_hooks(self):
        for key in ['apps','hooks','mcpServers','skills']:
            with self.subTest(key=key):
                edit_manifest(self.root, **{key:'./unexpected.json'})
                self.assertIn('FORBIDDEN_FILE',self.codes())
                make_package(self.root)

    def test_reject_nested_app_reference(self):
        edit_manifest(self.root, extensions={'com.openai':{'apps':'./.app.json'}})
        self.assertIn('FORBIDDEN_FILE', self.codes())

    def test_reject_path_escape(self):
        self.append('\n[escape](../../../secret.md)\n')
        self.assertIn('PATH_ESCAPE', self.codes())

    def test_percent_encoded_path_escape(self):
        self.append('\n[escape](%2e%2e/%2e%2e/%2e%2e/secret.md)\n')
        self.assertIn('PATH_ESCAPE', self.codes())

    def test_reject_absolute_and_windows_paths(self):
        for link in ['/etc/passwd', r'C:\secret.md', '//host/share.md', 'javascript:alert']:
            with self.subTest(link=link):
                make_package(self.root)
                self.append(f'\n[escape]({link})\n')
                self.assertIn('PATH_ESCAPE', self.codes())

    def test_reject_symlink(self):
        (self.root/'assets').mkdir()
        (self.root/'assets/link.md').symlink_to(self.root/SKILL)
        self.assertIn('NON_REGULAR_FILE', self.codes())

    def test_reject_directory_symlink(self):
        (self.root/'skills/link').symlink_to(self.root/'skills/investigate-company-role', target_is_directory=True)
        self.assertIn('NON_REGULAR_FILE', self.codes())

    def test_reject_root_symlink(self):
        alias=Path(self.tmp.name)/'alias'; alias.symlink_to(self.root, target_is_directory=True)
        self.assertIn('NON_REGULAR_FILE', {x['code'] for x in validate_package(alias, mode='draft')})

    @unittest.skipUnless(hasattr(os,'mkfifo'), 'FIFO test needs POSIX')
    def test_reject_fifo_without_blocking(self):
        os.mkfifo(self.root/'pipe')
        self.assertIn('NON_REGULAR_FILE', self.codes())

    def test_reject_compatibility_overlay(self):
        p=self.root/'.codex-plugin/plugin.json';p.parent.mkdir();p.write_text('{}')
        self.assertIn('FORBIDDEN_FILE', self.codes())

    def test_invalid_manifest_json(self):
        (self.root/'plugin.json').write_text('{broken')
        self.assertIn('MANIFEST_SHAPE', self.codes())

    def test_manifest_duplicate_key(self):
        p=self.root/'plugin.json';text=p.read_text();p.write_text(text[:-1]+',"name":"different"}')
        self.assertIn('MANIFEST_SHAPE', self.codes())

    def test_invalid_manifest_types_and_version(self):
        for fields in [{'name':[]},{'version':'next'},{'description':''},{'extensions':[]}]:
            with self.subTest(fields=fields):
                make_package(self.root); edit_manifest(self.root,**fields)
                self.assertIn('MANIFEST_SHAPE', self.codes())

    def test_skill_frontmatter_name_matches_folder(self):
        p=self.root/SKILL;p.write_text(p.read_text().replace('name: investigate-company-role','name: wrong-name'))
        self.assertIn('MANIFEST_SHAPE', self.codes())

    def test_skill_frontmatter_missing_description(self):
        (self.root/SKILL).write_text('---\nname: investigate-company-role\n---\nBody')
        self.assertIn('MANIFEST_SHAPE', self.codes())

    def test_no_skills_rejected(self):
        (self.root/SKILL).unlink()
        self.assertIn('MISSING_REFERENCE', self.codes())

    def test_approved_hashes_match(self):
        self.assertEqual(validate_package(self.root,mode='draft',approved=approve(self.root)),[])

    def test_changed_bytes_rejected(self):
        hashes=approve(self.root); self.append('PRIVATE_CANARY_T18')
        self.assertIn('UNAPPROVED_CONTENT', self.codes(approved=hashes))

    def test_invalid_approved_path_rejected(self):
        hashes=approve(self.root);hashes['../secret.md']='a'*64
        self.assertIn('PATH_ESCAPE',self.codes(approved=hashes))

    def test_release_needs_metadata_and_approval(self):
        codes={x['code'] for x in validate_package(self.root,mode='release')}
        self.assertIn('RELEASE_METADATA',codes)
        self.assertIn('UNAPPROVED_CONTENT',codes)

    def test_draft_has_no_icon_requirement(self):
        self.assertFalse((self.root/'assets/icon.png').exists())
        self.assertEqual(self.codes(),set())

    def test_invalid_mode_fails(self):
        with self.assertRaises(ValueError):validate_package(self.root,mode='other')

    def test_malformed_external_url_is_diagnostic_not_crash(self):
        self.append('\n[broken](https://[bad)\n')
        self.assertIn('PATH_ESCAPE',self.codes())

    def test_all_presentation_references_checked(self):
        edit_manifest(self.root,extensions={'com.openai':{'interface':{'screenshots':['./assets/missing.png']}}})
        self.assertIn('MISSING_REFERENCE',self.codes())

    def test_frontmatter_rejects_non_string_yaml_scalar(self):
        p=self.root/SKILL
        p.write_text('---\nname: investigate-company-role\ndescription: []\n---\nBody\n')
        self.assertIn('MANIFEST_SHAPE',self.codes())

    def test_cli_success_and_invalid_content(self):
        script=Path(__file__).resolve().parents[1]/'tools/check_package.py'
        command=[sys.executable,str(script),'--root',str(self.root),'--mode','draft']
        p=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout)['findings'],[])
        self.append('\n[missing](not-exist.md)')
        p=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
        self.assertIn('MISSING_REFERENCE',p.stdout)

if __name__=='__main__':unittest.main()
