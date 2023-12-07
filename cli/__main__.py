import typer
import time
import json
from typing_extensions import Annotated
from loguru import logger
from prometheus_performance_insights_exporter.pi_client import PiClient
from prometheus_performance_insights_exporter.rds_helper import RdsHelper

app = typer.Typer()


@app.command()
def get_rds_metrics(
    instance_id: Annotated[
        str,
        typer.Option(
            help="RDS database instance id. It is NOT DBInstanceIdentifier, it is the DB ResourceId"
        ),
    ]
):
    logger.debug(f"Getting 'DbiResourceId' from instance id {instance_id}.")
    db_resource_id = RdsHelper.get_db_resource_id(instance_id)
    logger.info(f"DbiResourceId for instance id {instance_id} is {db_resource_id}")

    pi_client = PiClient(db_resource_id)
    response = pi_client.get_rds_metrics(
        [{"Metric": "db.load.avg", "GroupBy": {"Group": "db.user"}}],
        start_time=time.time() - (5 * 60),
        end_time=time.time(),
    )

    result = {}

    for m in response['MetricList']:

        if "Dimensions" not in m["Key"].keys():
            continue

        db_user = m["Key"]["Dimensions"]["db.user.name"]

        result[db_user] = m["DataPoints"][0]["Value"]

    logger.warning(json.dumps(result, indent=4, sort_keys=True, default=str))


@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")


if __name__ == "__main__":
    app()
