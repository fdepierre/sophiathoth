#!/bin/bash

#########################################################################
# SophiaThoth Keycloak Setup Script
#########################################################################
#
# This script sets up Keycloak for the SophiaThoth application with:
#   - A dedicated realm named 'sophiathoth'
#   - A client for the web UI
#   - Default roles and users
#
# DEFAULT USERS AND CREDENTIALS:
# -----------------------------
# 1. Keycloak Admin:
#    - Username: admin
#    - Password: admin
#    - Role: Keycloak administrator
#    - Access: Full admin access to Keycloak
#
# 2. Knowledge User:
#    - Username: knowledge_user
#    - Password: Test@123
#    - Role: knowledge_role
#    - Access: Access to create and update content in the application
#
# 3. Regular User:
#    - Username: user_user
#    - Password: Test@123
#    - Role: user
#    - Access: Limited access to knowledge query and basic features
#
# ROLES DESCRIPTION:
# -----------------
# - knowledge_role: Access to create and update content in the application
# - user: Limited access to knowledge query and basic features
#
# HOW TO USE:
# ----------
# 1. Start the Keycloak service using docker-compose
# 2. Run this script: ./setup-keycloak.sh
# 3. Login to the web UI with one of the default users
#
# SECURITY NOTE:
# -------------
# These are default development credentials. In a production environment,
# you should change these passwords immediately after setup.
#
#########################################################################

# Wait for Keycloak to be ready
echo "Waiting for Keycloak to be ready..."
until curl -s http://localhost:8080 > /dev/null; do
    echo "Waiting for Keycloak..."
    sleep 5
done
echo "Keycloak is up and running!"

# Get admin token
echo "Getting admin token..."
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8080/realms/master/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin" \
  -d "password=admin" \
  -d "grant_type=password" \
  -d "client_id=admin-cli" | jq -r '.access_token')

if [ -z "$ADMIN_TOKEN" ] || [ "$ADMIN_TOKEN" == "null" ]; then
  echo "Failed to get admin token. Check Keycloak admin credentials."
  exit 1
fi

echo "Admin token obtained successfully."

# Check if realm exists
REALM_EXISTS=$(curl -s -X GET http://localhost:8080/admin/realms \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.[] | select(.realm=="sophiathoth") | .realm')

if [ "$REALM_EXISTS" == "sophiathoth" ]; then
  echo "Realm 'sophiathoth' already exists."
else
  # Create realm
  echo "Creating 'sophiathoth' realm..."
  curl -s -X POST http://localhost:8080/admin/realms \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "realm": "sophiathoth",
      "enabled": true,
      "displayName": "SophiaThoth",
      "displayNameHtml": "<div class=\"kc-logo-text\"><span>SophiaThoth</span></div>",
      "registrationAllowed": true,
      "resetPasswordAllowed": true,
      "loginWithEmailAllowed": true,
      "duplicateEmailsAllowed": false,
      "sslRequired": "external"
    }'
  
  echo "Realm 'sophiathoth' created successfully."
fi

# Check if client exists
CLIENT_EXISTS=$(curl -s -X GET http://localhost:8080/admin/realms/sophiathoth/clients \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.[] | select(.clientId=="web-ui") | .clientId')

if [ "$CLIENT_EXISTS" == "web-ui" ]; then
  echo "Client 'web-ui' already exists."
else
  # Create client
  echo "Creating 'web-ui' client..."
  CLIENT_RESPONSE=$(curl -s -X POST http://localhost:8080/admin/realms/sophiathoth/clients \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "clientId": "web-ui",
      "name": "Web UI",
      "description": "SophiaThoth Web UI",
      "enabled": true,
      "publicClient": true,
      "redirectUris": ["http://localhost:3000/*"],
      "webOrigins": ["http://localhost:3000"],
      "standardFlowEnabled": true,
      "implicitFlowEnabled": false,
      "directAccessGrantsEnabled": true,
      "serviceAccountsEnabled": false,
      "authorizationServicesEnabled": false,
      "fullScopeAllowed": true
    }')
  
  echo "Client 'web-ui' created successfully."
fi

# Remove all existing users except the admin
echo "Removing existing users..."

# Get all users in the realm
USERS=$(curl -s -X GET "http://localhost:8080/admin/realms/sophiathoth/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.[] | .id + ":" + .username')

# Loop through users and delete them (except admin)
for USER in $USERS; do
  USER_ID=$(echo $USER | cut -d':' -f1)
  USERNAME=$(echo $USER | cut -d':' -f2)
  
  if [ "$USERNAME" != "admin" ]; then
    echo "Removing user '$USERNAME'..."
    curl -s -X DELETE "http://localhost:8080/admin/realms/sophiathoth/users/$USER_ID" \
      -H "Authorization: Bearer $ADMIN_TOKEN"
    echo "User '$USERNAME' removed successfully."
  fi
done

# Remove existing roles (except default ones)
echo "Removing existing custom roles..."

# Get all roles in the realm
ROLES=$(curl -s -X GET "http://localhost:8080/admin/realms/sophiathoth/roles" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.[] | .name')

# Loop through roles and delete custom ones
for ROLE in $ROLES; do
  # Skip default roles
  if [[ "$ROLE" != "default-roles-sophiathoth" && "$ROLE" != "offline_access" && "$ROLE" != "uma_authorization" ]]; then
    echo "Removing role '$ROLE'..."
    curl -s -X DELETE "http://localhost:8080/admin/realms/sophiathoth/roles/$ROLE" \
      -H "Authorization: Bearer $ADMIN_TOKEN"
    echo "Role '$ROLE' removed successfully."
  fi
done

# Create 'knowledge_role' role if it doesn't exist
ROLE_EXISTS=$(curl -s -X GET "http://localhost:8080/admin/realms/sophiathoth/roles" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.[] | select(.name=="knowledge_role") | .name')

if [ "$ROLE_EXISTS" == "knowledge_role" ]; then
  echo "Role 'knowledge_role' already exists."
else
  # Create knowledge_role
  echo "Creating 'knowledge_role'..."
  curl -s -X POST "http://localhost:8080/admin/realms/sophiathoth/roles" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "knowledge_role",
      "description": "Role with access to create and update content in the application"
    }'
  echo "Role 'knowledge_role' created successfully."
fi

# Create 'user' role if it doesn't exist
ROLE_EXISTS=$(curl -s -X GET "http://localhost:8080/admin/realms/sophiathoth/roles" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.[] | select(.name=="user") | .name')

if [ "$ROLE_EXISTS" == "user" ]; then
  echo "Role 'user' already exists."
else
  # Create user role
  echo "Creating 'user' role..."
  curl -s -X POST "http://localhost:8080/admin/realms/sophiathoth/roles" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "user",
      "description": "Regular user role with limited access"
    }'
  echo "Role 'user' created successfully."
fi

# Create Knowledge user
echo "Creating Knowledge user..."
KNOWLEDGE_USER_RESPONSE=$(curl -s -X POST "http://localhost:8080/admin/realms/sophiathoth/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "knowledge_user",
    "email": "knowledge_user@example.com",
    "firstName": "Knowledge",
    "lastName": "User",
    "enabled": true,
    "emailVerified": true,
    "credentials": [
      {
        "type": "password",
        "value": "Test@123",
        "temporary": false
      }
    ]
  }')

# Get the user ID to assign role
KNOWLEDGE_USER_ID=$(curl -s -X GET "http://localhost:8080/admin/realms/sophiathoth/users?username=knowledge_user" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.[0].id')

# Get the role ID for knowledge_role
KNOWLEDGE_ROLE_ID=$(curl -s -X GET "http://localhost:8080/admin/realms/sophiathoth/roles" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.[] | select(.name=="knowledge_role") | .id')

# Assign knowledge_role to the user
curl -s -X POST "http://localhost:8080/admin/realms/sophiathoth/users/$KNOWLEDGE_USER_ID/role-mappings/realm" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "[{\
    \"id\": \"$KNOWLEDGE_ROLE_ID\",\
    \"name\": \"knowledge_role\",\
    \"clientRole\": false,\
    \"composite\": false\
  }]"

echo "Knowledge user created and role assigned successfully."

# Create Regular user
echo "Creating Regular user..."
USER_USER_RESPONSE=$(curl -s -X POST "http://localhost:8080/admin/realms/sophiathoth/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user_user",
    "email": "user_user@example.com",
    "firstName": "Regular",
    "lastName": "User",
    "enabled": true,
    "emailVerified": true,
    "credentials": [
      {
        "type": "password",
        "value": "Test@123",
        "temporary": false
      }
    ]
  }')

# Get the user ID to assign role
USER_USER_ID=$(curl -s -X GET "http://localhost:8080/admin/realms/sophiathoth/users?username=user_user" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.[0].id')

# Get the role ID for user
USER_ROLE_ID=$(curl -s -X GET "http://localhost:8080/admin/realms/sophiathoth/roles" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.[] | select(.name=="user") | .id')

# Assign user role to the user
curl -s -X POST "http://localhost:8080/admin/realms/sophiathoth/users/$USER_USER_ID/role-mappings/realm" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "[{\
    \"id\": \"$USER_ROLE_ID\",\
    \"name\": \"user\",\
    \"clientRole\": false,\
    \"composite\": false\
  }]"

echo "Regular user created and role assigned successfully."

echo "Keycloak setup completed successfully!"
