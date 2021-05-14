import importlib
import json
import logging

from netpalm.backend.core.confload.confload import config
from netpalm.backend.plugins.utilities.jinja2.j2 import render_j2template

log = logging.getLogger(__name__)

class webhook_runner:

    def __init__(self, whook_payload):
        self.webhook_dir_path = config.custom_webhooks
        self.webhook_raw_name = whook_payload.get("name")
        self.webhook_args = whook_payload.get("args", False)
        if not self.webhook_raw_name:
            self.webhook_name = config.default_webhook_name
        self.webhook_name = self.webhook_dir_path.replace("/",".") + self.webhook_raw_name
        self.webhook_j2_name = whook_payload.get("j2template")

    def webhook_exec(self, job_data):
        try:
            log.info(f"webhook_exec: importing f"{self.webhook_name}")
            module = importlib.import_module(self.webhook_name)
            run_whook = getattr(module, "run_webhook")
            job_data["webhook_args"] = self.webhook_args
            whook_data = job_data
            log.info(f"webhook_exec: webhook data loaded f"{whook_data}")
            if self.webhook_j2_name:
                log.info(f"webhook_exec: rendering webhook j2 template f"{self.webhook_j2_name}")
                res = render_j2template(
                                        self.webhook_j2_name,
                                        template_type="webhook",
                                        kwargs=job_data
                                        )
                whook_data = json.loads(
                    res["data"]["task_result"]["template_render_result"]
                    )
            res = run_whook(payload=whook_data)
            return res
        except Exception as e:
            log.error(f"webhook_exec: webhook run failure f"{e}")
            return e


def exec_webhook_func(jobdata, webhook_payload):
    webhook = webhook_runner(whook_payload=webhook_payload)
    execute = webhook.webhook_exec(job_data=jobdata)
    return execute
