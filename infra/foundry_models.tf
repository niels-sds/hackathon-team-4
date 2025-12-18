resource "azapi_resource" "chat_model_deployment" {
  type      = "Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview"
  name      = "chatmodel"
  parent_id = azapi_resource.foundry.id
  tags      = local.tags_azapi
  body = {
    properties = {
      currentCapacity = 25
      model = {
        format  = "OpenAI"
        name    = "gpt-4o"
        version = "2024-08-06"
      }
      raiPolicyName = "Microsoft.DefaultV2"
    }
    sku = {
      capacity = 50
      name     = "GlobalStandard"
    }
  }
}
