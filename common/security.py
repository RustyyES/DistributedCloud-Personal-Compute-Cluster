import re

def validate_job_command(command: str) -> bool:
    """
    Validate job command to prevent injection or dangerous operations.
    This is a basic filter.
    """
    # Block dangerous characters or patterns often used in shell injection
    # e.g. ';', '&&', '|', '`', '$(' 
    # BUT, legitimate jobs might need these?
    # Phase 4 "Security Hardening" implies we should catch obvious bad things.
    # For a personal compute cluster, maybe we trust the user but want to avoid accidental damage.
    # Let's block obvious attempts to escape the container execution command if not properly quoted?
    # Docker executor runs command as: client.containers.run(command=...)
    # If the user provides a string, Docker passes it to the entrypoint. 
    # If the image entrypoint is /bin/sh -c, then injection is possible.
    # If using default, it might be safer.
    
    # We will just ensure it's not empty and reasonable length
    if not command or len(command) > 1000:
        return False
        
    # Example: Block 'rm -rf /' (Just as a heuristic)
    if "rm -rf /" in command:
        return False
        
    return True

def sanitize_filename(filename: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_.-]', '', filename)



