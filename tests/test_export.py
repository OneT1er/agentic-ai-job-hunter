import os
import tempfile
from pathlib import Path

from src.export import export_to_csv


class TestExportToCsv:
    def test_export_single_job(self):
        jobs = [
            {
                "title": "AI工程师",
                "company": "字节跳动",
                "location": "北京",
                "salary": "30-60K",
                "tech_tags": ["PyTorch", "LLM"],
                "requirements": "熟悉大模型",
                "job_url": "https://example.com/1",
                "source": "牛客网",
            }
        ]
        tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w", encoding="utf-8-sig")
        with tmp as f:
            f.close()
            export_to_csv(jobs, f.name)
            content = Path(f.name).read_text(encoding="utf-8-sig")
            os.unlink(f.name)

        assert "AI工程师" in content
        assert "PyTorch, LLM" in content
        assert "字节跳动" in content

    def test_export_empty_list(self):
        export_to_csv([], "nonexistent.csv")
        assert not Path("nonexistent.csv").exists()

    def test_tech_tags_flattening(self):
        jobs = [
            {
                "title": "ML Engineer",
                "company": "A",
                "location": "上海",
                "salary": "面议",
                "tech_tags": ["TensorFlow", "Keras", "PyTorch"],
                "requirements": "",
                "job_url": "",
                "source": "",
            }
        ]
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            f.close()
            export_to_csv(jobs, f.name)
            content = Path(f.name).read_text(encoding="utf-8-sig")
            os.unlink(f.name)

        assert "TensorFlow, Keras, PyTorch" in content
