# PythonSV Infrastructure Setup

Step-by-step record of how the infrastructure was set up, so it can be reproduced or modified in the future.

## MongoDB Atlas

### Account & Organization

1. Created a new MongoDB Atlas account at https://cloud.mongodb.com using Google sign-in with `kevinturcios@pythonsv.com`
2. Renamed the auto-created organization from "Kevin's Org - 2026-04-23" to **PythonSV**
   - Organization Settings > Edit Organization Name
3. Renamed the auto-created project from "Project 0" to **pythonsv**
   - Project Settings > Edit Project Name

### Cluster

1. Created a **Free** (M0) cluster:
   - Name: `pythonsv` (cannot be changed after creation)
   - Provider: AWS
   - Region: N. Virginia (us-east-1) -- closest available free-tier region to El Salvador
2. During setup, Atlas auto-created:
   - DB user: `kevinturcios_db_user` with atlasAdmin permissions
   - IP access list entry for the current IP address
3. Connection string format: `mongodb+srv://kevinturcios_db_user:<password>@pythonsv.7ujjozc.mongodb.net/<database>?appName=pythonsv`

### Network Access

Added `0.0.0.0/0` to the IP access list (allow all) as a temporary measure. This will be replaced with the NAT Gateway's static IP once the VNet setup is complete (see Azure section below).

### Data Migration (from old cluster)

Old cluster: `pythonsv.akiq03k.mongodb.net` (personal account, turcioskevinr@gmail.com)
New cluster: `pythonsv.7ujjozc.mongodb.net` (PythonSV org account, kevinturcios@pythonsv.com)

```bash
# Dump from old cluster
mongodump --uri="mongodb+srv://turcioskevinr:<old-password>@pythonsv.akiq03k.mongodb.net/pythonsv" --out=./mongodump-export

# Restore to new cluster
mongorestore --uri="mongodb+srv://kevinturcios_db_user:<new-password>@pythonsv.7ujjozc.mongodb.net" ./mongodump-export
```

Database: `pythonsv`, Collection: `signups` (fields: name, email, role)

### Post-migration

1. Update `MONGO_URI` in `.env` to point to the new cluster
2. Update the `MONGO_URI` GitHub secret in PythonElSalvador/python_sv
3. Verify scripts work: `python scripts/query_signups.py`

## Azure Infrastructure

### Resource Group

- Name: `pythonsv`
- Location: East US

### Azure Container Registry (ACR)

- Name: `pythonsvcr`
- URL: `pythonsvcr.azurecr.io`
- Image: `pythonsv` (tags: `latest`, `staging`, `staging-<sha>`, `<sha>`)

### VNet + NAT Gateway (for static outbound IP)

Why: Azure Container Apps on the consumption plan use a shared pool of 300+ outbound IPs that can rotate. To restrict MongoDB Atlas access to a single IP (instead of `0.0.0.0/0`), all outbound traffic is routed through a NAT Gateway with a static public IP.

```bash
# 1. Create VNet with Container Apps subnet
az network vnet create \
  --name pythonsv-vnet \
  --resource-group pythonsv \
  --location eastus \
  --address-prefix 10.0.0.0/16

az network vnet subnet create \
  --name container-apps-subnet \
  --resource-group pythonsv \
  --vnet-name pythonsv-vnet \
  --address-prefix 10.0.0.0/23

# 2. Create static public IP for NAT Gateway
az network public-ip create \
  --name pythonsv-nat-ip \
  --resource-group pythonsv \
  --location eastus \
  --sku Standard \
  --allocation-method Static

# 3. Create NAT Gateway and attach the public IP
az network nat gateway create \
  --name pythonsv-nat-gw \
  --resource-group pythonsv \
  --location eastus \
  --public-ip-addresses pythonsv-nat-ip \
  --idle-timeout 4

# 4. Associate NAT Gateway with the subnet
az network vnet subnet update \
  --name container-apps-subnet \
  --resource-group pythonsv \
  --vnet-name pythonsv-vnet \
  --nat-gateway pythonsv-nat-gw

# 5. Get the subnet resource ID (needed for the Container Apps environment)
az network vnet subnet show \
  --name container-apps-subnet \
  --resource-group pythonsv \
  --vnet-name pythonsv-vnet \
  --query id -o tsv

# 6. Get the static public IP (add this to Atlas IP access list)
az network public-ip show \
  --name pythonsv-nat-ip \
  --resource-group pythonsv \
  --query ipAddress -o tsv
```

### Container Apps Environment

The environment must be created inside the VNet to use the NAT Gateway. Existing environments cannot be moved into a VNet -- they must be recreated.

```bash
# Delegate the subnet to Container Apps (required before creating the environment)
az network vnet subnet update \
  --name container-apps-subnet \
  --resource-group pythonsv \
  --vnet-name pythonsv-vnet \
  --delegations Microsoft.App/environments

# Create new environment in the VNet
az containerapp env create \
  --name pythonsv-env-v2 \
  --resource-group pythonsv \
  --location southcentralus \
  --infrastructure-subnet-resource-id <subnet-id-from-step-5>
```

### Container Apps

#### Production (pythonsv)

```bash
az containerapp create \
  --name pythonsv \
  --resource-group pythonsv \
  --environment pythonsv-env-v2 \
  --image pythonsvcr.azurecr.io/pythonsv:latest \
  --registry-server pythonsvcr.azurecr.io \
  --target-port 8000 \
  --ingress external \
  --cpu 0.25 \
  --memory 0.5Gi \
  --min-replicas 0 \
  --max-replicas 2 \
  --env-vars \
    ALLOWED_HOSTS='["pythonsv.com","www.pythonsv.com"]' \
    BASE_URL=https://pythonsv.com \
    LOG_LEVEL=INFO \
    WEB_CONCURRENCY=1 \
    RESEND_API_KEY=<resend-key>
```

Custom domains (after the app is created):
```bash
# Add managed certificates and bind domains
az containerapp hostname add --name pythonsv --resource-group pythonsv --hostname pythonsv.com
az containerapp hostname bind --name pythonsv --resource-group pythonsv --hostname pythonsv.com --environment pythonsv-env-v2 --validation-method HTTP

az containerapp hostname add --name pythonsv --resource-group pythonsv --hostname www.pythonsv.com
az containerapp hostname bind --name pythonsv --resource-group pythonsv --hostname www.pythonsv.com --environment pythonsv-env-v2 --validation-method CNAME
```

#### Staging (pythonsv-staging)

```bash
az containerapp create \
  --name pythonsv-staging \
  --resource-group pythonsv \
  --environment pythonsv-env-v2 \
  --image pythonsvcr.azurecr.io/pythonsv:latest \
  --registry-server pythonsvcr.azurecr.io \
  --target-port 8000 \
  --ingress external \
  --cpu 0.25 \
  --memory 0.5Gi \
  --min-replicas 0 \
  --max-replicas 1 \
  --env-vars \
    ALLOWED_HOSTS='["pythonsv-staging.agreeablefield-59184fdd.southcentralus.azurecontainerapps.io"]' \
    BASE_URL=https://pythonsv-staging.agreeablefield-59184fdd.southcentralus.azurecontainerapps.io \
    LOG_LEVEL=DEBUG \
    WEB_CONCURRENCY=1 \
    RESEND_API_KEY=
```

### DNS (Cloudflare)

- `pythonsv.com` -> CNAME to `pythonsv.agreeablefield-59184fdd.southcentralus.azurecontainerapps.io`
- `www.pythonsv.com` -> CNAME to `pythonsv.agreeablefield-59184fdd.southcentralus.azurecontainerapps.io`

Cloudflare proxy (orange cloud) must be disabled for managed cert validation to work. Root domains use HTTP validation; subdomains use CNAME validation. After certs are provisioned, proxy can be re-enabled if desired.

### Manual Deploy Commands

Production:
```bash
az containerapp update --name pythonsv --resource-group pythonsv --image pythonsvcr.azurecr.io/pythonsv:<sha>
```

Staging:
```bash
az containerapp update --name pythonsv-staging --resource-group pythonsv --image pythonsvcr.azurecr.io/pythonsv:staging-<sha>
```

## CI/CD (GitHub Actions)

Repository: `PythonElSalvador/python_sv`

### Workflows

| Workflow | Trigger | What it does |
|---|---|---|
| `ci.yml` | PRs to main | Lint + test |
| `deploy.yml` | Push to main | Lint + test + build + push to ACR |
| `staging.yml` | Push to staging branch | Same pipeline, tags as `staging`/`staging-<sha>` |

### GitHub Secrets

| Secret | Description |
|---|---|
| `ACR_USERNAME` | ACR admin username |
| `ACR_PASSWORD` | ACR admin password |
| `MONGO_URI` | MongoDB connection string |
| `AZURE_CREDENTIALS` | Service principal JSON (for auto-deploy, pending) |

### Auto-deploy (pending)

Blocked on service principal role assignment. See ROADMAP.md for details.

## Key Resources Reference

| Resource | Value |
|---|---|
| Production URL | https://pythonsv.com |
| Staging URL | https://pythonsv-staging.agreeablefield-59184fdd.southcentralus.azurecontainerapps.io |
| ACR | pythonsvcr.azurecr.io |
| Resource Group | pythonsv |
| Location | South Central US |
| VNet | pythonsv-vnet (10.0.0.0/16) |
| Subnet | container-apps-subnet (10.0.0.0/23) |
| NAT Gateway | pythonsv-nat-gw |
| NAT Public IP | pythonsv-nat-ip (4.151.106.157) |
| Container App (prod) | pythonsv |
| Container App (staging) | pythonsv-staging |
| Environment | pythonsv-env-v2 |
| Atlas Org | PythonSV (kevinturcios@pythonsv.com) |
| Atlas Cluster | pythonsv.7ujjozc.mongodb.net |
| GitHub Repo | PythonElSalvador/python_sv |
