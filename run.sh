#!/bin/bash


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

echo "$GIT_MESSASGE"

success "\nBuild triggered successfully."
