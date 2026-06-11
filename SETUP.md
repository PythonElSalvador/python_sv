# Configuración de infraestructura de PythonSV

Registro paso a paso de cómo se configuró la infraestructura, para que pueda reproducirse o modificarse en el futuro.

## MongoDB Atlas

### Cuenta y organización

1. Se creó una nueva cuenta de MongoDB Atlas en https://cloud.mongodb.com usando Google con `kevinturcios@pythonsv.com`
2. Se renombró la organización creada automáticamente de "Kevin's Org - 2026-04-23" a **PythonSV**
   - Configuración de organización > Editar nombre de organización
3. Se renombró el proyecto creado automáticamente de "Project 0" a **pythonsv**
   - Configuración del proyecto > Editar nombre del proyecto

### Clúster

1. Se creó un clúster **gratuito** (M0):
   - Nombre: `pythonsv` (no se puede cambiar después de la creación)
   - Proveedor: AWS
   - Región: N. Virginia (us-east-1) -- región de nivel gratuito más cercana disponible a El Salvador
2. Durante la configuración, Atlas creó automáticamente:
   - Usuario de BD: `kevinturcios_db_user` con permisos de atlasAdmin
   - Entrada en la lista de acceso por IP para la dirección IP actual
3. Formato de cadena de conexión: `mongodb+srv://kevinturcios_db_user:<password>@pythonsv.7ujjozc.mongodb.net/<database>?appName=pythonsv`

### Acceso de red

Se agregó `0.0.0.0/0` a la lista de acceso por IP (permitir todo) como medida temporal. Será reemplazado con la IP estática del NAT Gateway una vez que la configuración de la VNet esté completa (ver sección de Azure más abajo).

### Migración de datos (desde el clúster anterior)

Clúster anterior: `pythonsv.akiq03k.mongodb.net` (cuenta personal, turcioskevinr@gmail.com)
Nuevo clúster: `pythonsv.7ujjozc.mongodb.net` (cuenta de la org PythonSV, kevinturcios@pythonsv.com)

```bash
# Exportar desde el clúster anterior
mongodump --uri="mongodb+srv://turcioskevinr:<old-password>@pythonsv.akiq03k.mongodb.net/pythonsv" --out=./mongodump-export

# Restaurar en el nuevo clúster
mongorestore --uri="mongodb+srv://kevinturcios_db_user:<new-password>@pythonsv.7ujjozc.mongodb.net" ./mongodump-export
```

Base de datos: `pythonsv`, Colección: `signups` (campos: name, email, role)

### Post-migración

1. Actualizar `MONGO_URI` en `.env` para apuntar al nuevo clúster
2. Actualizar el secreto `MONGO_URI` de GitHub en PythonElSalvador/python_sv
3. Verificar que los scripts funcionen: `python scripts/query_signups.py`

## Infraestructura en Azure

### Grupo de recursos

- Nombre: `pythonsv`
- Ubicación: East US

### Azure Container Registry (ACR)

- Nombre: `pythonsvcr`
- URL: `pythonsvcr.azurecr.io`
- Imagen: `pythonsv` (etiquetas: `latest`, `staging`, `staging-<sha>`, `<sha>`)

### VNet + NAT Gateway (para IP de salida estática)

Por qué: Las Container Apps de Azure en el plan de consumo usan un conjunto compartido de más de 300 IPs de salida que pueden rotar. Para restringir el acceso a MongoDB Atlas a una sola IP (en lugar de `0.0.0.0/0`), todo el tráfico saliente se enruta a través de un NAT Gateway con una IP pública estática.

```bash
# 1. Crear VNet con subred para Container Apps
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

# 2. Crear IP pública estática para el NAT Gateway
az network public-ip create \
  --name pythonsv-nat-ip \
  --resource-group pythonsv \
  --location eastus \
  --sku Standard \
  --allocation-method Static

# 3. Crear el NAT Gateway y asociar la IP pública
az network nat gateway create \
  --name pythonsv-nat-gw \
  --resource-group pythonsv \
  --location eastus \
  --public-ip-addresses pythonsv-nat-ip \
  --idle-timeout 4

# 4. Asociar el NAT Gateway con la subred
az network vnet subnet update \
  --name container-apps-subnet \
  --resource-group pythonsv \
  --vnet-name pythonsv-vnet \
  --nat-gateway pythonsv-nat-gw

# 5. Obtener el ID de recurso de la subred (necesario para el entorno de Container Apps)
az network vnet subnet show \
  --name container-apps-subnet \
  --resource-group pythonsv \
  --vnet-name pythonsv-vnet \
  --query id -o tsv

# 6. Obtener la IP pública estática (agregar esta IP a la lista de acceso de Atlas)
az network public-ip show \
  --name pythonsv-nat-ip \
  --resource-group pythonsv \
  --query ipAddress -o tsv
```

### Entorno de Container Apps

El entorno debe crearse dentro de la VNet para usar el NAT Gateway. Los entornos existentes no pueden moverse a una VNet — deben recrearse.

```bash
# Delegar la subred a Container Apps (requerido antes de crear el entorno)
az network vnet subnet update \
  --name container-apps-subnet \
  --resource-group pythonsv \
  --vnet-name pythonsv-vnet \
  --delegations Microsoft.App/environments

# Crear nuevo entorno en la VNet
az containerapp env create \
  --name pythonsv-env-v2 \
  --resource-group pythonsv \
  --location southcentralus \
  --infrastructure-subnet-resource-id <subnet-id-from-step-5>
```

### Container Apps

#### Producción (pythonsv)

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

Dominios personalizados (después de crear la app):
```bash
# Agregar certificados administrados y vincular dominios
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

- `pythonsv.com` -> CNAME a `pythonsv.agreeablefield-59184fdd.southcentralus.azurecontainerapps.io`
- `www.pythonsv.com` -> CNAME a `pythonsv.agreeablefield-59184fdd.southcentralus.azurecontainerapps.io`

El proxy de Cloudflare (nube naranja) debe estar desactivado para que la validación del certificado administrado funcione. Los dominios raíz usan validación HTTP; los subdominios usan validación CNAME. Una vez aprovisionados los certificados, el proxy puede reactivarse si se desea.

### Comandos de despliegue manual

Producción:
```bash
az containerapp update --name pythonsv --resource-group pythonsv --image pythonsvcr.azurecr.io/pythonsv:<sha>
```

Staging:
```bash
az containerapp update --name pythonsv-staging --resource-group pythonsv --image pythonsvcr.azurecr.io/pythonsv:staging-<sha>
```

## CI/CD (GitHub Actions)

Repositorio: `PythonElSalvador/python_sv`

### Workflows

| Workflow | Disparador | Qué hace |
|---|---|---|
| `ci.yml` | PRs a main | Linting + pruebas |
| `deploy.yml` | Push a main | Linting + pruebas + build + push a ACR |
| `staging.yml` | Push a la rama staging | Mismo pipeline, etiquetas como `staging`/`staging-<sha>` |

### Secretos de GitHub

| Secreto | Descripción |
|---|---|
| `ACR_USERNAME` | Usuario administrador del ACR |
| `ACR_PASSWORD` | Contraseña del administrador del ACR |
| `MONGO_URI` | Cadena de conexión a MongoDB |
| `AZURE_CREDENTIALS` | JSON del service principal (para auto-despliegue, pendiente) |

### Auto-despliegue (pendiente)

Bloqueado por la asignación de roles del service principal. Ver ROADMAP.md para más detalles.

## Referencia de recursos clave

| Recurso | Valor |
|---|---|
| URL de producción | https://pythonsv.com |
| URL de staging | https://pythonsv-staging.agreeablefield-59184fdd.southcentralus.azurecontainerapps.io |
| ACR | pythonsvcr.azurecr.io |
| Grupo de recursos | pythonsv |
| Ubicación | South Central US |
| VNet | pythonsv-vnet (10.0.0.0/16) |
| Subred | container-apps-subnet (10.0.0.0/23) |
| NAT Gateway | pythonsv-nat-gw |
| IP pública NAT | pythonsv-nat-ip (4.151.106.157) |
| Container App (prod) | pythonsv |
| Container App (staging) | pythonsv-staging |
| Entorno | pythonsv-env-v2 |
| Org Atlas | PythonSV (kevinturcios@pythonsv.com) |
| Clúster Atlas | pythonsv.7ujjozc.mongodb.net |
| Repositorio GitHub | PythonElSalvador/python_sv |