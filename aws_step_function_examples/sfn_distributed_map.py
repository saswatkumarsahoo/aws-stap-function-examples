from aws_cdk import Stack, aws_stepfunctions as sfn, aws_iam as iam, aws_s3 as s3, aws_s3_deployment as s3_deplyment
from constructs import Construct
import json


class SfnDistributedMap(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # bucket for testing object tagging
        bucket = s3.Bucket(self, "bucket", 
                           bucket_name="stepfunctions-dist-map-2023") # provide a unique bucket name

        # upload some sample files for testing tagging of objecs using step function
        assets = s3_deplyment.Source.asset('./sample_files')
        s3_deplyment.BucketDeployment(self, "upload-sample-files",destination_bucket=bucket, sources=[assets])

        iam_role = iam.Role(
            self,
            "sfn-role-dist-map",
            assumed_by=iam.ServicePrincipal("states.amazonaws.com"),
        )
        bucket.grant_read_write(iam_role)

        # read the sfn defination from asl JSON file
        with open("./src/asl/distributed_map.json") as definition_file:
            definition = definition_file.read()

        state_machine = sfn.CfnStateMachine(
            self,
            "sfn-distributed-map",
            definition_string=str(definition),
            role_arn=iam_role.role_arn,
            state_machine_name="distributed-map-example",
            state_machine_type="STANDARD",
        )

        # permissiones needed to start child execution of the map state
        policy_doc = iam.PolicyDocument.from_json(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "FirstStatement",
                        "Effect": "Allow",
                        "Action": ["states:StartExecution"],
                        "Resource": f"{state_machine.attr_arn}*",
                    }
                ],
            }
        )
        new_policy = iam.Policy(self, "MyNewPolicy", document=policy_doc)
        iam_role.attach_inline_policy(new_policy)