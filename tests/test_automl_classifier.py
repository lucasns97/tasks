import os
import unittest
import uuid

import papermill

from tests import datasets, deployments

EXPERIMENT_ID = str(uuid.uuid4())
OPERATOR_ID = str(uuid.uuid4())
RUN_ID = str(uuid.uuid4())


class TestAutoMLClassifier(unittest.TestCase):

    def setUp(self):
        # Set environment variables needed to run notebooks
        os.environ["EXPERIMENT_ID"] = EXPERIMENT_ID
        os.environ["OPERATOR_ID"] = OPERATOR_ID
        os.environ["RUN_ID"] = RUN_ID

        datasets.iris()
        datasets.titanic()

        os.chdir("tasks/automl-classifier")

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

                time_left_for_this_task=30,
                per_run_time_limit=30,
                ensemble_size=5,

                method="predict_proba",
            ),
        )

        papermill.execute_notebook(
            "Deployment.ipynb",
            "/dev/null",
        )
        proc = deployments.run()
        data = datasets.iris_testdata()
        response = deployments.test(data=data)
        if response is None:
            print(proc.stderr.read().decode(), flush=True)
        os.kill(proc.pid, 9)
        names = response["names"]
        ndarray = response["ndarray"]
        self.assertEqual(len(ndarray[0]), 8)  # 4 features + 1 class + 3 probas
        self.assertEqual(len(names), 8)

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

                time_left_for_this_task=30,
                per_run_time_limit=30,
                ensemble_size=5,

                method="predict_proba",
            ),
        )

        papermill.execute_notebook(
            "Deployment.ipynb",
            "/dev/null",
        )
        proc = deployments.run()
        data = datasets.titanic_testdata()
        response = deployments.test(data=data)
        if response is None:
            print(proc.stderr.read().decode(), flush=True)
        os.kill(proc.pid, 9)
        names = response["names"]
        ndarray = response["ndarray"]
        self.assertEqual(len(ndarray[0]), 15)  # 12 features + 1 class + 2 probas
        self.assertEqual(len(names), 15)
