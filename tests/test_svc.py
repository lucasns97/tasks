import os
import unittest
import uuid

import papermill

from tests import datasets

EXPERIMENT_ID = str(uuid.uuid4())
OPERATOR_ID = str(uuid.uuid4())
RUN_ID = str(uuid.uuid4())


class TestSVC(unittest.TestCase):

    def setUp(self):
        # Set environment variables needed to run notebooks
        os.environ["EXPERIMENT_ID"] = EXPERIMENT_ID
        os.environ["OPERATOR_ID"] = OPERATOR_ID
        os.environ["RUN_ID"] = RUN_ID

        datasets.iris()
        datasets.titanic()

        os.chdir("tasks/svc")

    def tearDown(self):
        datasets.clean()
        os.chdir("../../")

    def test_experiment_iris(self):
        papermill.execute_notebook(
            "Experiment.ipynb",
            "/dev/null",
            parameters=dict(
                dataset="/tmp/data/iris.csv",
                target="Species",

                filter_type="remover",
                model_features="",

                one_hot_features="",

                C=1.0,
                kernel="rbf",
                degree=3,
                gamma="auto",
                probability=True,
                max_iter=-1,

                method="predict_proba",
            ),
        )

    def test_experiment_titanic(self):
        papermill.execute_notebook(
            "Experiment.ipynb",
            "/dev/null",
            parameters=dict(
                dataset="/tmp/data/titanic.csv",
                target="Survived",

                filter_type="remover",
                model_features="",

                one_hot_features="",

                C=1.0,
                kernel="rbf",
                degree=3,
                gamma="auto",
                probability=True,
                max_iter=-1,

                method="predict_proba",
            ),
        )
