#!/bin/bash

# Define the directory containing the text files
agent_prompts_directory="../../prompt-creator/prompts-text"

# Loop through all .txt files in the directory
for filename in "$agent_prompts_directory"/*.txt; do
    # Read the first line for the site
    read -r site < "$filename"

    # Read the remaining lines as tasks
    while IFS= read -r line; do
        # Skip the first line containing the site
        if [ "$line" == "$site" ]; then
            continue
        fi

        # Call the ground truth (with adblocker)
        python vimgpt.py "$site" "$line" "true"

        # Run with dark patterns
        python vimgpt.py "$site" "$line" "false"

    done < "$filename"
done
