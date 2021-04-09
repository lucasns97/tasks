# -*- coding: utf-8 -*-
import json
import os

from database import insert_task
from notebook import create_persistent_volume_claim, create_config_map, copy_files_inside_pod, \
    parse_parameters, patch_notebook_server, set_notebook_metadata, uuid_alpha

CONFIG_PATH = "/tasks/config.json"


def create_tasks():
    """
    Inserts tasks in database, allocates volumes, mounts them in notebook server.
    """
    with open(CONFIG_PATH) as f:
        tasks = json.load(f)

    volume_mounts = []

    for task in tasks:
        arguments = task["arguments"]
        commands = task["commands"]
        description = task["description"]
        name = task["name"]
        tags = task["tags"]
        image = task["image"]
        path = task.get("path")
        cpu_limit = task.get("cpuLimit")
        cpu_request = task.get("cpuRequest")
        memory_limit = task.get("memoryLimit")
        memory_request = task.get("memoryRequest")
        parameters = []

        if path:
            experiment_notebook_path = "Experiment.ipynb"
            deployment_notebook_path = "Deployment.ipynb"
            parameters = parse_parameters(f"{path}/{experiment_notebook_path}")
        else:
            experiment_notebook_path = None
            deployment_notebook_path = None

        task_id = insert_task(
            name=name,
            description=description,
            tags=tags,
            image=image,
            commands=commands,
            arguments=arguments,
            is_default=True,
            parameters=parameters,
            experiment_notebook_path=experiment_notebook_path,
            deployment_notebook_path=deployment_notebook_path,
            cpu_limit=cpu_limit,
            cpu_request=cpu_request,
            memory_limit=memory_limit,
            memory_request=memory_request,
        )
        task["task_id"] = task_id

        volume_name = f"vol-task-{task_id}"
        mount_path = f"/home/jovyan/tasks/{name}"

        create_persistent_volume_claim(
            name=volume_name,
        )
        volume_mounts.append({
            "name": volume_name,
            "mount_path": mount_path,
        })

        if "MONITORING" in tags:
            file_content = open(f"{path}/Experiment.ipynb", "r").read()
            create_config_map(task_id=task_id, experiment_notebook_content=file_content)

    # Adds volume mount to the notebook server
    patch_notebook_server(volume_mounts)

    # Copies task files and artifacts
    for task in tasks:
        name = task["name"]
        path = task.get("path")
        if path:
            copy_files_inside_pod(
                local_path=path,
                destination_path=name,
                task_name=name,
            )

            experiment_id = uuid_alpha()
            operator_id = uuid_alpha()

            if os.path.exists(f"{path}/Experiment.ipynb"):
                notebook_path = f"{name}/Experiment.ipynb"
                set_notebook_metadata(
                    notebook_path=notebook_path,
                    task_id=task_id,
                    experiment_id=experiment_id,
                    operator_id=operator_id,
                )

            if os.path.exists(f"{path}/Deployment.ipynb"):
                notebook_path = f"{name}/Deployment.ipynb"
                set_notebook_metadata(
                    notebook_path=notebook_path,
                    task_id=task_id,
                    experiment_id=experiment_id,
                    operator_id=operator_id,
                )


def main():
    """
    Job that creates tasks in PlatIAgro from a config file.
    """
    create_tasks()

    print("done!", flush=True)


if __name__ == "__main__":
    main()
