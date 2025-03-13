#!/bin/bash
set -e

# Configuration
ENV=${1:-"local"}
MIGRATION_NAME=${2:-""}
ACTION=${3:-"generate"} # generate, apply, or verify

# Load environment variables
if [ "$ENV" != "local" ]; then
    if [ ! -f ".env.$ENV" ]; then
        echo "Error: .env.$ENV file not found"
        exit 1
    fi
    source ".env.$ENV"
fi

# Functions
generate_migration() {
    echo "Generating migration for $ENV environment..."
    cd backend

    if [ -z "$MIGRATION_NAME" ]; then
        echo "Error: Migration name required"
        exit 1
    fi

    # Generate migration file
    alembic revision --autogenerate -m "$MIGRATION_NAME"

    # Generate SQL
    MIGRATION_FILE="../supabase/migrations/${ENV}/$(date +%Y%m%d%H%M%S)_${MIGRATION_NAME}.sql"
    mkdir -p "../supabase/migrations/${ENV}"
    alembic upgrade head --sql > "$MIGRATION_FILE"

    echo "Migration generated: $MIGRATION_FILE"
}

verify_migration() {
    echo "Verifying migration for $ENV environment..."

    # Create temporary database for verification
    if [ "$ENV" != "local" ]; then
        TEMP_DB="verify_${ENV}_$(date +%s)"
        createdb "$TEMP_DB"

        # Apply migration to temp db
        PGDATABASE="$TEMP_DB" alembic upgrade head

        # Verify schema
        PGDATABASE="$TEMP_DB" alembic check

        # Cleanup
        dropdb "$TEMP_DB"
    else
        supabase db reset
    fi
}

apply_migration() {
    echo "Applying migration to $ENV environment..."

    if [ "$ENV" = "production" ]; then
        read -p "⚠️ Are you sure you want to apply migrations to PRODUCTION? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    if [ "$ENV" = "local" ]; then
        supabase db reset
    else
        supabase link --project-ref "$SUPABASE_PROJECT_ID"
        supabase db push
    fi
}

# Main execution
case $ACTION in
    "generate")
        generate_migration
        ;;
    "verify")
        verify_migration
        ;;
    "apply")
        verify_migration
        apply_migration
        ;;
    *)
        echo "Invalid action: $ACTION"
        exit 1
        ;;
esac
