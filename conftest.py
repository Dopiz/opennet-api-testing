import logging
import os
from pathlib import Path

import pytest

logger = logging.getLogger("automation")


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="default",
        help="Config environment name (default, staging, etc)",
    )


def pytest_configure(config):
    from utils.helper import ConfigHelper

    config_helper = ConfigHelper(env=config.getoption("--env"))

    config.artifact_path = Path(__file__).parent / "artifacts"
    os.makedirs(config.artifact_path, exist_ok=True)

    logger.info("Env:", config.getoption("--env"))
    logger.info("Config:", config_helper.all)

    log_path = config.artifact_path / "auto_test.log"
    handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def pytest_runtest_setup(item):
    # Do something you may want to execute before test run
    ...


def pytest_runtest_teardown(item):
    # Do something you may want to execute after test run
    ...


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    # Store result on node so fixtures can check pass/fail during teardown
    setattr(item, f"rep_{report.when}", report)

    if report.when == "call":
        logger.info(f"Result: {report.outcome.upper()}")
        if report.failed:
            logger.error(f"Failure reason: {report.longreprtext}")

        # Inject allure description and clean up parameters via allure listener
        listener = item.config.pluginmanager.get_plugin("allure_listener")
        if listener:
            for key, value in item.user_properties:
                if key == "allure_description" and value:
                    listener.add_description(value)

            # Remove pytest's auto-generated "data" parameter from allure
            uuid = listener._cache.get(item.nodeid)
            if uuid:
                test_result = listener.allure_logger.get_test(uuid)
                if test_result:
                    test_result.parameters = [p for p in test_result.parameters if p.name != "data"]
