from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import AKS, VMScaleSets
from diagrams.azure.network import VirtualNetworks, Subnets, ApplicationGateway, Firewall
from diagrams.azure.compute import ContainerRegistries
from diagrams.azure.security import KeyVaults
from diagrams.azure.analytics import LogAnalyticsWorkspaces
from diagrams.azure.general import Usericon as Users
from diagrams.azure.devops import ApplicationInsights
from diagrams.k8s.compute import Pod
from diagrams.k8s.controlplane import API
from diagrams.onprem.vcs import Github
# from diagrams.onprem.cd import ArgoCD
from diagrams.custom import Custom

graph_attr = {
    "splines": "ortho",
    "nodesep": "0.8",
    "ranksep": "1.0",
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.5"
}

with Diagram("Azure Kubernetes Cluster", show=False, filename="azure-k8s/k8s_cluster_arch", outformat=["png", "dot"], graph_attr=graph_attr):
    
    users = Users("Users")
    
    with Cluster("Azure Subscription"):
        
        # External Container Registry
        with Cluster("RG: ics-containers"):
            acr = ContainerRegistries("incora")

        with Cluster("RG: <cluster_name>-rg"):
            
            # Monitoring
            law = LogAnalyticsWorkspaces("log-analytics")
            
            # KeyVault
            kv = KeyVaults("key-vault")

            with Cluster("VNet: <cluster_name>-vnet (10.61.6.32/27)"):
                
                # Subnet 1: AKS
                with Cluster("Subnet: <cluster_name>-subnet (10.61.6.32/28)"):
                    
                    aks = AKS("AKS Cluster\n<cluster_name>")
                    
                    # Node Pools (Logical representation)
                    with Cluster("Node Pools"):
                        np_sys = VMScaleSets("System Pool\n(3 nodes)")
                        np_user = VMScaleSets("User Pool\n(2 nodes)")
                        np_ci = VMScaleSets("CI Pool\n(2 nodes)")
                        
                        aks - [np_sys, np_user, np_ci]

                    # K8s Internals
                    with Cluster("K8s Namespaces"):
                        
                        with Cluster("ingress-system"):
                            ingress = Pod("Ingress Controller")
                        
                        with Cluster("argo"):
                            argo = Pod("ArgoCD")

                # Subnet 2: Secondary
                with Cluster("Subnet: Secondary (10.61.6.48/29)"):
                    secondary = Subnets("Secondary")

    # Flow
    users >> aks
    aks >> acr
    aks >> kv
    aks >> law
    
    # Internal Logic
    ingress >> np_sys
    argo >> np_ci

    # Integrations
    # acr << Edge(label="AcrPull") << np_sys 
