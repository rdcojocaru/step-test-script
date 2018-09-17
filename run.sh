#!/bin/bash

GIT_MESSAGE = "DEFAULT MESSAGE"

if [ "$WERCKER_TRIGGER_TEST_MESSAGE" ]; then
	GIT_MESSAGE="$WERCKER_TRIGGER_TEST_MESSAGE"
fi

generate_post_data()
{
  cat <<EOF
{
  "message": "$GIT_MESSAGE"
}
EOF
}

echo "JSON: $(generate_post_data)"

echo "$GIT_MESSAGE"

success "\nBuild triggered successfully."
