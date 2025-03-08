#!/bin/bash

#########################################################################
# SophiaThoth Keycloak Login Test Script
#########################################################################
#
# This script tests the login functionality for the users
# created in the setup-keycloak.sh script.
#
#########################################################################

echo "Testing Keycloak login for configured users..."

# Test login for Admin user
echo -e "\n1. Testing login for Admin user (admin_user)..."
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8080/realms/sophiathoth/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin_user" \
  -d "password=Test@123" \
  -d "grant_type=password" \
  -d "client_id=web-ui" | jq -r '.access_token')

if [ -z "$ADMIN_TOKEN" ] || [ "$ADMIN_TOKEN" == "null" ]; then
  echo "❌ Failed to login as admin_user. Error details:"
  curl -v -X POST http://localhost:8080/realms/sophiathoth/protocol/openid-connect/token \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin_user" \
    -d "password=Test@123" \
    -d "grant_type=password" \
    -d "client_id=web-ui" 2>&1 | grep -E "< HTTP|error"
else
  echo "✅ Successfully logged in as admin_user!"
  echo "Token: ${ADMIN_TOKEN:0:20}... (truncated)"
  
  # Verify admin role in token
  ROLES=$(echo $ADMIN_TOKEN | jq -R 'split(".") | .[1] | @base64d | fromjson | .realm_access.roles' 2>/dev/null)
  if [[ $ROLES == *"\"admin\""* ]]; then
    echo "✅ Token contains 'admin' role as expected"
  else
    echo "❌ Token does not contain 'admin' role. Roles found: $ROLES"
  fi
fi

# Test login for Regular user
echo -e "\n2. Testing login for Regular user (user_user)..."
USER_TOKEN=$(curl -s -X POST http://localhost:8080/realms/sophiathoth/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user_user" \
  -d "password=Test@123" \
  -d "grant_type=password" \
  -d "client_id=web-ui" | jq -r '.access_token')

if [ -z "$USER_TOKEN" ] || [ "$USER_TOKEN" == "null" ]; then
  echo "❌ Failed to login as user_user. Error details:"
  curl -v -X POST http://localhost:8080/realms/sophiathoth/protocol/openid-connect/token \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=user_user" \
    -d "password=Test@123" \
    -d "grant_type=password" \
    -d "client_id=web-ui" 2>&1 | grep -E "< HTTP|error"
else
  echo "✅ Successfully logged in as user_user!"
  echo "Token: ${USER_TOKEN:0:20}... (truncated)"
  
  # Verify user role in token
  ROLES=$(echo $USER_TOKEN | jq -R 'split(".") | .[1] | @base64d | fromjson | .realm_access.roles' 2>/dev/null)
  if [[ $ROLES == *"\"user\""* ]]; then
    echo "✅ Token contains 'user' role as expected"
  else
    echo "❌ Token does not contain 'user' role. Roles found: $ROLES"
  fi
fi

echo -e "\nLogin tests completed!"
