from diagrams import Diagram, Cluster, Edge
from diagrams.azure.network import (
    VirtualNetworks, Subnets, LoadBalancers,
    ApplicationGateway, FrontDoors, Firewall,
    NetworkSecurityGroupsClassic, PrivateEndpoint
)
from diagrams.azure.compute import (
    AppServices, FunctionApps, ContainerInstances
)
from diagrams.azure.web import AppServicePlans
from diagrams.azure.database import SQLServers, SQLDatabases
from diagrams.azure.storage import StorageAccounts
from diagrams.azure.security import KeyVaults
from diagrams.azure.integration import ServiceBus
from diagrams.azure.analytics import LogAnalyticsWorkspaces
from diagrams.azure.devops import ApplicationInsights
from diagrams.azure.general import Usericon as Users
import subprocess
import os

# Graph Attributes for Clean Layout
graph_attr = {
    "splines": "ortho",
    "nodesep": "0.8",
    "ranksep": "1.2",
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.5"
}

# Cluster Colors
frontend_color = "#E3F2FD"
backend_color = "#E8F5E9"
data_color = "#FFF3E0"
monitoring_color = "#F3E5F5"

with Diagram("Contoso Architecture", show=False, filename="diagrams/contoso_architecture", outformat=["png", "dot"], graph_attr=graph_attr):
    
    users = Users("Users")

    with Cluster("Azure Subscription"):
        
        with Cluster("Monitoring", graph_attr={"bgcolor": monitoring_color}):
            law = LogAnalyticsWorkspaces("law-contoso-prod")
            appi = ApplicationInsights("appi-contoso")

        with Cluster("Virtual Network: vnet-contoso-auea-001 (10.10.0.0/16)"):
            
            # Firewall (Global to VNet/Hub - simplified placement)
            fw = Firewall("azfw-contoso")

            with Cluster("snet-frontend (10.10.1.0/24)", graph_attr={"bgcolor": frontend_color}):
                agw = ApplicationGateway("agw-contoso")
                asp_front = AppServicePlans("asp-contoso-prod")
                web_app = AppServices("app-frontend-portal")
                nsg_front = NetworkSecurityGroupsClassic("NSG-Front")

            with Cluster("snet-backend (10.10.2.0/24)", graph_attr={"bgcolor": backend_color}):
                asp_back = AppServicePlans("asp-contoso-backend")
                api_app = AppServices("app-order-api")
                func_app = FunctionApps("func-order-processor")
                sb = ServiceBus("sb-contoso-orders")
                nsg_back = NetworkSecurityGroupsClassic("NSG-Back")

            with Cluster("snet-data (10.10.3.0/24)", graph_attr={"bgcolor": data_color}):
                sql_server = SQLServers("sqlsrv-contoso")
                sql_db = SQLDatabases("sqldb-orders")
                storage = StorageAccounts("stcontosodata001")
                kv = KeyVaults("kv-contoso-prod")
                nsg_data = NetworkSecurityGroupsClassic("NSG-Data")
                
                # Private Endpoints Visual Representation
                pe_sql = PrivateEndpoint("PE-SQL")
                pe_st = PrivateEndpoint("PE-Storage")
                pe_kv = PrivateEndpoint("PE-KeyVault")

        # Global Resources
        fd = FrontDoors("afd-contoso")

    # Connections
    users >> fd >> agw >> web_app
    web_app >> api_app
    api_app >> pe_sql
    api_app >> pe_st
    
    # Function App Flow
    func_app >> sb >> pe_sql

    # Key Vault Access
    [web_app, api_app, func_app] >> pe_kv

    # Monitoring
    [web_app, api_app, func_app, sql_db, storage, kv, fw, agw] >> law
    [web_app, api_app, func_app] >> appi

    # Firewall Outbound
    [web_app, api_app, func_app] >> fw

    # Internal Connections associations
    pe_sql - sql_db
    pe_st - storage
    pe_kv - kv
    sql_server - sql_db

# Auto-convert to Draw.io
try:
    print("Converting DOT to Draw.io...")
    subprocess.run([
        "graphviz2drawio", 
        "diagrams/contoso_architecture.dot", 
        "-o", 
        "diagrams/contoso_architecture.drawio"
    ], check=True)
    print("Conversion successful!")
except Exception as e:
    print(f"Error converting to draw.io: {e}")
    print("Ensure graphviz2drawio is installed.")
