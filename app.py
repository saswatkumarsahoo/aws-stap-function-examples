#!/usr/bin/env python3
import os

import aws_cdk as cdk

from aws_step_function_examples.sfn_distributed_map import SfnDistributedMap


app = cdk.App()
SfnDistributedMap(app, "SfnDistributedMap")
app.synth()
