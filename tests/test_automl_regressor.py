import os
import unittest
import uuid

import papermill

from tests import datasets

EXPERIMENT_ID = str(uuid.uuid4())
OPERATOR_ID = str(uuid.uuid4())
RUN_ID = str(uuid.uuid4())


class TestAutoMLRegressor(unittest.TestCase):

    def setUp(self):
        # Set environment variables needed to run notebooks
        os.environ["EXPERIMENT_ID"] = EXPERIMENT_ID
        os.environ["OPERATOR_ID"] = OPERATOR_ID
        os.environ["RUN_ID"] = RUN_ID

        datasets.boston()

        os.chdir("tasks/automl-regressor")

    def tearDown(self):
        datasets.clean()
        os.chdir("../../")

    def test_boston(self):
        papermill.execute_notebook(
            "Experiment.ipynb",
            "/dev/null",
            parameters=dict(
                dataset="/tmp/data/boston.csv",
                target="medv",

                filter_type="remover",
                model_features="",

                one_hot_features="",

                time_left_for_this_task=30,
                per_run_time_limit=30,
                ensemble_size=5,
            ),
        )
