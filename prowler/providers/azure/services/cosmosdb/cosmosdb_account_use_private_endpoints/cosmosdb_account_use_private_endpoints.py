from prowler.lib.check.models import Check, Check_Report_Azure
from prowler.providers.azure.services.cosmosdb.cosmosdb_client import cosmosdb_client


class cosmosdb_account_use_private_endpoints(Check):
    def execute(self) -> Check_Report_Azure:
        findings = []
        for subscription, accounts in cosmosdb_client.accounts.items():
            for account in accounts:
                report = Check_Report_Azure(metadata=self.metadata(), resource=account)
                report.subscription = subscription
                report.status = "FAIL"
                report.status_extended = f"CosmosDB account {account.name} from subscription {subscription} is not using private endpoints connections"
                if account.private_endpoint_connections:
                    report.status = "PASS"
                    report.status_extended = f"CosmosDB account {account.name} from subscription {subscription} is using private endpoints connections"
                findings.append(report)

        return findings
