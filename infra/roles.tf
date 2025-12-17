resource "azurerm_role_assignment" "user_cognitive_services_open_ai_contributor" {
  scope                = azapi_resource.foundry.id
  role_definition_name = "Cognitive Services OpenAI Contributor"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_role_assignment" "user_azure_ai_user" {
  scope                = azapi_resource.foundry.id
  role_definition_name = "Azure AI User"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_role_assignment" "user_azure_ai_project_manager" {
  scope                = azapi_resource.foundry.id
  role_definition_name = "Azure AI Project Manager"
  principal_id         = data.azurerm_client_config.current.object_id
}

# Additional users - Cognitive Services OpenAI Contributor
resource "azurerm_role_assignment" "additional_users_openai_contributor" {
  for_each             = toset(var.additional_user_object_ids)
  scope                = azapi_resource.foundry.id
  role_definition_name = "Cognitive Services OpenAI Contributor"
  principal_id         = each.value
}

# Additional users - Azure AI User
resource "azurerm_role_assignment" "additional_users_ai_user" {
  for_each             = toset(var.additional_user_object_ids)
  scope                = azapi_resource.foundry.id
  role_definition_name = "Azure AI User"
  principal_id         = each.value
}

# Additional users - Azure AI Project Manager
resource "azurerm_role_assignment" "additional_users_project_manager" {
  for_each             = toset(var.additional_user_object_ids)
  scope                = azapi_resource.foundry.id
  role_definition_name = "Azure AI Project Manager"
  principal_id         = each.value
}