# Roadmap

## Auto-deploy to Azure Container Apps

The CD pipeline (`.github/workflows/deploy.yml`) builds and pushes to ACR but doesn't auto-deploy. A service principal exists but has no role assignment.

**Status:** Blocked — need subscription owner to grant permissions.

### What's already done

- Service principal `github-pythonsv` exists (appId: `4493f559-a697-4db9-b881-6a11851bbcd3`)
- ACR credentials stored as GitHub secrets (`ACR_USERNAME`, `ACR_PASSWORD`)
- Build + push workflow works on push to main

### Steps to unblock

1. Ask subscription owner (Saurabh / `saurabhtacit.onmicrosoft.com`) to run:
   ```
   az role assignment create \
     --assignee 4493f559-a697-4db9-b881-6a11851bbcd3 \
     --role Contributor \
     --scope /subscriptions/923d59dc-54b7-47d4-ab81-c7cb9061dac5/resourceGroups/pythonsv
   ```

2. Generate a credential for the SP:
   ```
   az ad sp credential reset --id 4493f559-a697-4db9-b881-6a11851bbcd3
   ```

3. Store the JSON output as GitHub secret `AZURE_CREDENTIALS`

4. Add a deploy job to `.github/workflows/deploy.yml`:
   ```yaml
   deploy:
     needs: build
     runs-on: ubuntu-latest
     steps:
       - uses: azure/login@v2
         with:
           creds: ${{ secrets.AZURE_CREDENTIALS }}
       - run: |
           az containerapp update \
             --name pythonsv \
             --resource-group pythonsv \
             --image pythonsvcr.azurecr.io/pythonsv:${{ github.sha }}
   ```

5. Add a deploy job to `.github/workflows/staging.yml`:
   ```yaml
   deploy:
     needs: build
     runs-on: ubuntu-latest
     steps:
       - uses: azure/login@v2
         with:
           creds: ${{ secrets.AZURE_CREDENTIALS }}
       - run: |
           az containerapp update \
             --name pythonsv-staging \
             --resource-group pythonsv \
             --image pythonsvcr.azurecr.io/pythonsv:staging-${{ github.sha }}
   ```

## Manual deploy (current workaround)

Production:
```
az containerapp update --name pythonsv --resource-group pythonsv --image pythonsvcr.azurecr.io/pythonsv:<sha>
```

Staging:
```
az containerapp update --name pythonsv-staging --resource-group pythonsv --image pythonsvcr.azurecr.io/pythonsv:staging-<sha>
```
