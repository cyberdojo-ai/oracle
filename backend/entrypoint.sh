#!/bin/bash


usage() {
    cat << EOF
    Usage: entrypoint.sh [options] <command>

    This script is the entrypoint for the application.
    If no command is provided, the API will be started. otherwise, the command will be executed.

    Commands:
        init_db             Initialize the database schema.
        start_api           Start the API server.
        start_mcp           Start the MCP server.
        start_enrichment    Start the enrichment server.
        <command>           Execute a command in the application context.

    Options:
        -h, --help      Show this help message and exit
        -d, --debug     Enable debug mode. Unsafe for production environments.

EOF
}

# Set default values
PORT=8000
WORKERS=1
NO_UPDATE_DB=${NO_UPDATE_DB:-''}

while [[ -n "$1" ]]; do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        -d|--debug)
            DEBUG=yes
            ;;
        -*|--*)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
        init_db)
            INIT_DB=yes
            break
            ;;
        start_api)
            # This is the default command, so we don't need to set a flag
            break
            ;;
        start_mcp)
            START_MCP=yes
            break
            ;;
        start_enrichment)
            START_ENRICHMENT=yes
            break
            ;;
        *)
            EXECUTE_COMMAND=yes
            break
            ;;
    esac
    shift
done

# Set debug mode if enabled
if [[ -n "$DEBUG" ]]; then
    echo "WARNING: Debug mode is enabled. This should not be used in production."
    echo "Secrets may be exposed in the logs."
    set -x
fi


# Initialize the database if requested
if [[ -n "$INIT_DB" ]]; then
    echo "Initializing the database"
    alembic upgrade head
    exit 0
fi

# Execute command if provided
if [[ -n $EXECUTE_COMMAND ]]; then
    echo "Executing command: $1"
    exec $@
fi

# Update the database if requested
if [[ -z "$NO_UPDATE_DB" ]]; then
    echo "Updating the database"
    alembic upgrade head
fi

# Start the MCP server if requested
if [[ -n "$START_MCP" ]]; then
    echo "Starting the MCP server"
    exec python mcp-server.py
fi
if [[ -n "$START_ENRICHMENT" ]]; then
    echo "Starting the enrichment server"
    exec python enrichment-server.py
fi

# Start the API server
echo "Starting the API server"

exec python api-server.py
