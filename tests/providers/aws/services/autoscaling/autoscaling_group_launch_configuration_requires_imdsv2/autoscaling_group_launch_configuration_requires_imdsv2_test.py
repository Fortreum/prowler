from unittest import mock

from boto3 import client
from moto import mock_aws

from tests.providers.aws.utils import AWS_REGION_US_EAST_1, set_mocked_aws_provider


class Test_autoscaling_group_launch_configuration_requires_imdsv2:
    @mock_aws
    def test_no_autoscaling(self):
        autoscaling_client = client("autoscaling", region_name=AWS_REGION_US_EAST_1)
        autoscaling_client.groups = []

        from prowler.providers.aws.services.autoscaling.autoscaling_service import (
            AutoScaling,
        )

        aws_provider = set_mocked_aws_provider([AWS_REGION_US_EAST_1])

        with mock.patch(
            "prowler.providers.common.provider.Provider.get_global_provider",
            return_value=aws_provider,
        ), mock.patch(
            "prowler.providers.aws.services.autoscaling.autoscaling_group_launch_configuration_requires_imdsv2.autoscaling_group_launch_configuration_requires_imdsv2.autoscaling_client",
            new=AutoScaling(aws_provider),
        ):
            # Test Check
            from prowler.providers.aws.services.autoscaling.autoscaling_group_launch_configuration_requires_imdsv2.autoscaling_group_launch_configuration_requires_imdsv2 import (
                autoscaling_group_launch_configuration_requires_imdsv2,
            )

            check = autoscaling_group_launch_configuration_requires_imdsv2()
            result = check.execute()

            assert len(result) == 0

    @mock_aws
    def test_groups_with_imdsv2_enabled_and_required(self):
        autoscaling_client = client("autoscaling", region_name=AWS_REGION_US_EAST_1)
        autoscaling_client.create_launch_configuration(
            LaunchConfigurationName="test",
            ImageId="ami-12c6146b",
            InstanceType="t1.micro",
            KeyName="the_keys",
            SecurityGroups=["default", "default2"],
            MetadataOptions={
                "HttpTokens": "required",
                "HttpPutResponseHopLimit": 123,
                "HttpEndpoint": "enabled",
            },
        )
        autoscaling_group_name = "my-autoscaling-group"
        autoscaling_client.create_auto_scaling_group(
            AutoScalingGroupName=autoscaling_group_name,
            LaunchConfigurationName="test",
            MinSize=0,
            MaxSize=0,
            DesiredCapacity=0,
            AvailabilityZones=["us-east-1a", "us-east-1b"],
        )

        autoscaling_group_arn = autoscaling_client.describe_auto_scaling_groups(
            AutoScalingGroupNames=[autoscaling_group_name]
        )["AutoScalingGroups"][0]["AutoScalingGroupARN"]

        from prowler.providers.aws.services.autoscaling.autoscaling_service import (
            AutoScaling,
        )

        aws_provider = set_mocked_aws_provider([AWS_REGION_US_EAST_1])

        with mock.patch(
            "prowler.providers.common.provider.Provider.get_global_provider",
            return_value=aws_provider,
        ), mock.patch(
            "prowler.providers.aws.services.autoscaling.autoscaling_group_launch_configuration_requires_imdsv2.autoscaling_group_launch_configuration_requires_imdsv2.autoscaling_client",
            new=AutoScaling(aws_provider),
        ):
            # Test Check
            from prowler.providers.aws.services.autoscaling.autoscaling_group_launch_configuration_requires_imdsv2.autoscaling_group_launch_configuration_requires_imdsv2 import (
                autoscaling_group_launch_configuration_requires_imdsv2,
            )

            check = autoscaling_group_launch_configuration_requires_imdsv2()
            result = check.execute()

            assert len(result) == 1
            assert result[0].status == "PASS"
            assert (
                result[0].status_extended
                == f"Autoscaling group {autoscaling_group_name} has IMDSv2 enabled and required."
            )
            assert result[0].resource_id == autoscaling_group_name
            assert result[0].resource_arn == autoscaling_group_arn
            assert result[0].region == AWS_REGION_US_EAST_1
            assert result[0].resource_tags == []

    @mock_aws
    def test_groups_without_launch_configuration(self):
        autoscaling_client = client("autoscaling", region_name=AWS_REGION_US_EAST_1)
        ec2_client = client("ec2", region_name=AWS_REGION_US_EAST_1)
        ec2_client.create_launch_template(
            LaunchTemplateName="test",
            LaunchTemplateData={
                "ImageId": "ami-12c6146b",
                "InstanceType": "t1.micro",
                "KeyName": "the_keys",
                "SecurityGroups": ["default", "default2"],
            },
        )
        autoscaling_group_name = "my-autoscaling-group"
        autoscaling_client.create_auto_scaling_group(
            AutoScalingGroupName=autoscaling_group_name,
            LaunchTemplate={"LaunchTemplateName": "test", "Version": "$Latest"},
            MinSize=0,
            MaxSize=0,
            DesiredCapacity=0,
            AvailabilityZones=["us-east-1a", "us-east-1b"],
        )

        autoscaling_group_arn = autoscaling_client.describe_auto_scaling_groups(
            AutoScalingGroupNames=[autoscaling_group_name]
        )["AutoScalingGroups"][0]["AutoScalingGroupARN"]

        from prowler.providers.aws.services.autoscaling.autoscaling_service import (
            AutoScaling,
        )

        aws_provider = set_mocked_aws_provider([AWS_REGION_US_EAST_1])

        with mock.patch(
            "prowler.providers.common.provider.Provider.get_global_provider",
            return_value=aws_provider,
        ), mock.patch(
            "prowler.providers.aws.services.autoscaling.autoscaling_group_launch_configuration_requires_imdsv2.autoscaling_group_launch_configuration_requires_imdsv2.autoscaling_client",
            new=AutoScaling(aws_provider),
        ):
            # Test Check
            from prowler.providers.aws.services.autoscaling.autoscaling_group_launch_configuration_requires_imdsv2.autoscaling_group_launch_configuration_requires_imdsv2 import (
                autoscaling_group_launch_configuration_requires_imdsv2,
            )

            check = autoscaling_group_launch_configuration_requires_imdsv2()
            result = check.execute()

            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert (
                result[0].status_extended
                == f"Autoscaling group {autoscaling_group_name} has IMDSv2 disabled or not required."
            )
            assert result[0].resource_id == autoscaling_group_name
            assert result[0].resource_tags == []
            assert result[0].resource_arn == autoscaling_group_arn

    @mock_aws
    def test_groups_with_imdsv2_disabled(self):
        autoscaling_client = client("autoscaling", region_name=AWS_REGION_US_EAST_1)
        autoscaling_client.create_launch_configuration(
            LaunchConfigurationName="test",
            ImageId="ami-12c6146b",
            InstanceType="t1.micro",
            KeyName="the_keys",
            SecurityGroups=["default", "default2"],
            MetadataOptions={
                "HttpTokens": "required",
                "HttpPutResponseHopLimit": 123,
                "HttpEndpoint": "disabled",
            },
        )
        autoscaling_group_name = "my-autoscaling-group"
        autoscaling_client.create_auto_scaling_group(
            AutoScalingGroupName=autoscaling_group_name,
            LaunchConfigurationName="test",
            MinSize=0,
            MaxSize=0,
            DesiredCapacity=0,
            AvailabilityZones=["us-east-1a", "us-east-1b"],
        )

        autoscaling_group_arn = autoscaling_client.describe_auto_scaling_groups(
            AutoScalingGroupNames=[autoscaling_group_name]
        )["AutoScalingGroups"][0]["AutoScalingGroupARN"]

        from prowler.providers.aws.services.autoscaling.autoscaling_service import (
            AutoScaling,
        )

        aws_provider = set_mocked_aws_provider([AWS_REGION_US_EAST_1])

        with mock.patch(
            "prowler.providers.common.provider.Provider.get_global_provider",
            return_value=aws_provider,
        ), mock.patch(
            "prowler.providers.aws.services.autoscaling.autoscaling_group_launch_configuration_requires_imdsv2.autoscaling_group_launch_configuration_requires_imdsv2.autoscaling_client",
            new=AutoScaling(aws_provider),
        ):
            # Test Check
            from prowler.providers.aws.services.autoscaling.autoscaling_group_launch_configuration_requires_imdsv2.autoscaling_group_launch_configuration_requires_imdsv2 import (
                autoscaling_group_launch_configuration_requires_imdsv2,
            )

            check = autoscaling_group_launch_configuration_requires_imdsv2()
            result = check.execute()

            assert len(result) == 1
            assert result[0].status == "PASS"
            assert (
                result[0].status_extended
                == f"Autoscaling group {autoscaling_group_name} has metadata service disabled."
            )
            assert result[0].resource_id == autoscaling_group_name
            assert result[0].resource_tags == []
            assert result[0].resource_arn == autoscaling_group_arn
