from src.state import JobExtraction


class TestJobExtraction:
    def test_valid_target_job(self):
        job = JobExtraction(
            is_target_job=True,
            title="AI工程师",
            company="字节跳动",
            location="北京",
            salary="30-60K",
            tech_tags=["PyTorch", "LLM"],
            requirements="熟悉大模型训练",
        )
        assert job.title == "AI工程师"
        assert job.company == "字节跳动"
        assert job.is_target_job is True

    def test_default_field_values(self):
        job = JobExtraction(is_target_job=True)
        assert job.title == ""
        assert job.location == "未知"
        assert job.salary == "面议"
        assert job.tech_tags == []

    def test_non_target_job_defaults(self):
        job = JobExtraction(is_target_job=False)
        assert job.title == ""
        assert job.company == ""
