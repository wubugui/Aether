"""Producer failures retain their new evidence without passing validation."""
import contextlib,io,json,os,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
from validation_manifest import ValidationRun,sha256

class FailedReportArchive(unittest.TestCase):
    def check_failure(self,body,exit_code,stderr='',fresh=True):
        with tempfile.TemporaryDirectory() as folder,contextlib.redirect_stdout(io.StringIO()):
            root=Path(folder);sink=root/'road.json';sink.write_text('previous')
            os.utime(sink,ns=(1_000_000_000,1_000_000_000))
            run=ValidationRun(root,'fixture')
            def execute(command,out,err,cwd=None):
                out.write_text('');err.write_text(stderr)
                if fresh:
                    sink.write_text(body);now=time.time_ns();os.utime(sink,ns=(now,now))
                return exit_code
            with patch.object(run,'execute',execute),self.assertRaises(ValueError):
                run.stage('road-surfaces',['fixture'],report=sink)
            stage=run.manifest['stages'][0]
            self.assertEqual(stage['status'],'failed');self.assertFalse(stage['passed'])
            self.assertNotIn('report_contract_passed',stage)
            self.assertEqual((run.directory/'previous-reports/road-surfaces.json').read_text(),'previous')
            if fresh:
                archived=run.directory/stage['report'];self.assertEqual(archived.read_text(),body)
                self.assertEqual(run.manifest['artifacts'][stage['report']]['sha256'],sha256(archived))
            else:
                self.assertNotIn('report',stage);self.assertFalse((run.directory/'reports/road-surfaces.json').exists())
    def test_nonzero_exit_keeps_failed_report(self):self.check_failure('{"passed":false,"failed_samples":419}',1)
    def test_logged_error_keeps_fresh_report(self):self.check_failure('{"passed":true}',0,'SCRIPT ERROR: fixture\n')
    def test_nonzero_exit_keeps_malformed_report(self):self.check_failure('{incomplete',1)
    def test_stale_sink_is_only_previous_evidence(self):self.check_failure('',1,fresh=False)

if __name__=='__main__':unittest.main()
