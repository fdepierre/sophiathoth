#!/bin/sh

# Recreate config file
rm -rf /usr/share/nginx/html/env-config.js
touch /usr/share/nginx/html/env-config.js

# Add assignment 
echo "window._env_ = {" >> /usr/share/nginx/html/env-config.js

# Debug: Print all environment variables to a log file
echo "Environment variables at startup:" > /usr/share/nginx/html/env-debug.log
env | sort >> /usr/share/nginx/html/env-debug.log

# Read each line in .env file
# Each line represents key=value pairs
env | grep REACT_APP_ | while read -r line
do
  # Split env variables by character `=`
  if printf '%s\n' "$line" | grep -q -e '='; then
    varname=$(printf '%s\n' "$line" | sed -e 's/=.*//')
    varvalue=$(printf '%s\n' "$line" | sed -e 's/^[^=]*=//')
  fi

  # Just use the value from the environment variable
  # No variable indirection in sh
  
  # Append configuration property to JS file
  echo "  $varname: \"$varvalue\"," >> /usr/share/nginx/html/env-config.js
  
  # Debug: Log each environment variable
  echo "Adding $varname = $varvalue" >> /usr/share/nginx/html/env-debug.log
done

# Add hardcoded values for debugging if environment variables are missing
if ! grep -q "REACT_APP_KEYCLOAK_URL" /usr/share/nginx/html/env-config.js; then
  echo "  REACT_APP_KEYCLOAK_URL: \"http://localhost:8080\"," >> /usr/share/nginx/html/env-config.js
  echo "WARNING: REACT_APP_KEYCLOAK_URL was missing, added default value" >> /usr/share/nginx/html/env-debug.log
fi

if ! grep -q "REACT_APP_KEYCLOAK_REALM" /usr/share/nginx/html/env-config.js; then
  echo "  REACT_APP_KEYCLOAK_REALM: \"tender-management\"," >> /usr/share/nginx/html/env-config.js
  echo "WARNING: REACT_APP_KEYCLOAK_REALM was missing, added default value" >> /usr/share/nginx/html/env-debug.log
fi

if ! grep -q "REACT_APP_KEYCLOAK_CLIENT_ID" /usr/share/nginx/html/env-config.js; then
  echo "  REACT_APP_KEYCLOAK_CLIENT_ID: \"web-ui\"," >> /usr/share/nginx/html/env-config.js
  echo "WARNING: REACT_APP_KEYCLOAK_CLIENT_ID was missing, added default value" >> /usr/share/nginx/html/env-debug.log
fi

echo "}" >> /usr/share/nginx/html/env-config.js

# Debug: Log the final env-config.js content
echo "Final env-config.js content:" >> /usr/share/nginx/html/env-debug.log
cat /usr/share/nginx/html/env-config.js >> /usr/share/nginx/html/env-debug.log

exec "$@"
