"""Public archive byte integrity and safe local output publication."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from support import make_package, approve, SKILL
try:
    import tools.build_package as builder
except ModuleNotFoundError:
    builder = None


class BuildPackageTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(builder, 'build_package is not implemented')
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.root=make_package(self.base/'package')
        self.output=self.base/'dist'/'plugin.zip'
        self.approved=approve(self.root)

    def build(self, output=None, **kwargs):
        return builder.build_package(self.root,output or self.output,mode='draft',approved=kwargs.get('approved',self.approved))

    def test_T18_unapproved_bytes_blocked(self):
        with (self.root/SKILL).open('a') as f:f.write('PRIVATE_CANARY_T18')
        with self.assertRaisesRegex(ValueError,'UNAPPROVED_CONTENT'):self.build()
        self.assertFalse(self.output.exists())

    def test_extra_file_not_approved(self):
        (self.root/'skills/investigate-company-role/notes.md').write_text('PRIVATE_CANARY_T18')
        with self.assertRaisesRegex(ValueError,'UNAPPROVED_CONTENT'):self.build()

    def test_missing_approved_file_blocked(self):
        (self.root/SKILL).unlink()
        with self.assertRaisesRegex(ValueError,'UNAPPROVED_CONTENT'):self.build()

    def test_zip_root_and_entries(self):
        result=self.build()
        self.assertEqual(result['file_count'],str(len(self.approved)))
        self.assertEqual(result['archive'],str(self.output.resolve()))
        self.assertEqual(result['sha256'],hashlib.sha256(self.output.read_bytes()).hexdigest())
        with zipfile.ZipFile(self.output) as z:
            self.assertEqual(set(z.namelist()),set(self.approved))
            self.assertIn('plugin.json',z.namelist())
            self.assertIsNone(z.testzip())
            for rel,digest in self.approved.items():
                self.assertEqual(hashlib.sha256(z.read(rel)).hexdigest(),digest)

    def test_build_failure_leaves_no_archive(self):
        (self.root/'plugin.json').write_text('not-json')
        with self.assertRaisesRegex(ValueError,'MANIFEST_SHAPE'):self.build()
        self.assertFalse(self.output.exists())

    def test_existing_archive_not_overwritten(self):
        self.output.parent.mkdir();self.output.write_bytes(b'original output')
        with self.assertRaises(FileExistsError):self.build()
        self.assertEqual(self.output.read_bytes(),b'original output')

    def test_existing_broken_symlink_not_overwritten(self):
        self.output.parent.mkdir();self.output.symlink_to(self.base/'missing')
        with self.assertRaises(FileExistsError):self.build()
        self.assertTrue(self.output.is_symlink())

    def test_output_inside_plugin_rejected(self):
        with self.assertRaisesRegex(ValueError,'PATH_ESCAPE'):
            self.build(self.root/'inside.zip')
        self.assertFalse((self.root/'inside.zip').exists())

    def test_archive_reproducible(self):
        a=self.build()
        b=self.build(self.base/'dist'/'other.zip')
        self.assertEqual(a['sha256'],b['sha256'])
        self.assertEqual(self.output.read_bytes(),(self.base/'dist/other.zip').read_bytes())

    def test_snapshot_bytes_used_after_source_change(self):
        original=builder.read_snapshot
        expected=(self.root/SKILL).read_bytes()
        def read_then_change(root):
            data,errors=original(root)
            (root/SKILL).write_bytes(expected+b'\nPRIVATE_CANARY_T18_AFTER_SNAPSHOT')
            return data,errors
        with patch.object(builder,'read_snapshot',side_effect=read_then_change):self.build()
        with zipfile.ZipFile(self.output) as z:self.assertEqual(z.read(SKILL),expected)
        self.assertIn(b'PRIVATE_CANARY_T18_AFTER_SNAPSHOT',(self.root/SKILL).read_bytes())

    def test_archive_write_failure_cleans_temp(self):
        with patch.object(builder.zipfile.ZipFile,'writestr',side_effect=OSError('simulated full disk')):
            with self.assertRaises(OSError):self.build()
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.output.parent.iterdir()),[])

    def test_atomic_publication_never_replaces_racing_file(self):
        def occupy_then_link(source,dest):
            Path(dest).write_bytes(b'competing file')
            raise FileExistsError('another writer won')
        with patch.object(builder.os,'link',side_effect=occupy_then_link):
            with self.assertRaises(FileExistsError):self.build()
        self.assertEqual(self.output.read_bytes(),b'competing file')
        self.assertEqual(list(self.output.parent.iterdir()),[self.output])

    def test_cli_success_and_existing_output_exit_two(self):
        approved_path=self.base/'approval.json';approved_path.write_text(json.dumps(self.approved))
        script=Path(__file__).resolve().parents[1]/'tools/build_package.py'
        command=[sys.executable,str(script),'--root',str(self.root),'--mode','draft','--approved',str(approved_path),'--output',str(self.output)]
        p=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout)['file_count'],'2')
        p=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
        self.assertIn('error',json.loads(p.stdout))

if __name__=='__main__':unittest.main()
