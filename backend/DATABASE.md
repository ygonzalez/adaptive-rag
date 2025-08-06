# PostgreSQL Database Setup for Adaptive RAG

This application uses PostgreSQL to store chat sessions and message history.

## Database Schema

The database consists of two main tables:

1. **chat_sessions**: Stores session information
   - `id` (UUID): Unique session identifier
   - `created_at`: Session creation timestamp
   - `updated_at`: Last update timestamp

2. **chat_messages**: Stores individual messages within sessions
   - `id` (UUID): Unique message identifier
   - `session_id`: Foreign key to chat_sessions
   - `timestamp`: Message timestamp
   - `question`: User's question
   - `answer`: AI's response
   - `used_web_search`: Boolean indicating if web search was used
   - `sources`: JSON array of source documents
   - `generation_attempts`: Number of generation attempts
   - `web_search_attempts`: Number of web search attempts

## Quick Setup

### Option 1: Using Docker Compose (Recommended)

1. Make sure Docker is installed
2. Run the entire stack:
   ```bash
   docker-compose up -d
   ```
   
This will:
- Start PostgreSQL on port 5432
- Create the database and user automatically
- Start the backend API on port 8000
- Start the frontend on port 5173

### Option 2: Local PostgreSQL Installation

1. **Install PostgreSQL**:
   ```bash
   # macOS with Homebrew
   brew install postgresql
   brew services start postgresql
   
   # Ubuntu/Debian
   sudo apt install postgresql postgresql-contrib
   sudo systemctl start postgresql
   ```

2. **Run the setup script**:
   ```bash
   ./setup_postgres.sh
   ```
   
   This creates:
   - Database: `adaptive_rag_db`
   
   **Note**: The script assumes you're using your existing PostgreSQL user credentials:
   - User: `yvettegonzalez` (your local PostgreSQL user)
   - Password: `lisi2013` (your local PostgreSQL password)

3. **Update your `.env` file**:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and ensure DATABASE_URL is set correctly
   ```

4. **Initialize the database tables**:
   ```bash
   cd backend
   python init_db.py
   ```

## Environment Configuration

Your `backend/.env` file must include:

```env
DATABASE_URL=postgresql://yvettegonzalez:lisi2013@localhost:5432/adaptive_rag_db
```

For Docker deployment, use:
```env
DATABASE_URL=postgresql://yvettegonzalez:lisi2013@postgres:5432/adaptive_rag_db
```

## Database Management

### Connect to PostgreSQL
```bash
psql -U yvettegonzalez -d adaptive_rag_db -h localhost
```

### Useful Queries

View recent messages:
```sql
SELECT 
    cm.timestamp,
    cm.question,
    LEFT(cm.answer, 100) as answer_preview,
    cm.used_web_search
FROM chat_messages cm
ORDER BY cm.timestamp DESC
LIMIT 10;
```

Session statistics:
```sql
SELECT 
    cs.id,
    COUNT(cm.id) as message_count,
    MIN(cm.timestamp) as first_message,
    MAX(cm.timestamp) as last_message
FROM chat_sessions cs
LEFT JOIN chat_messages cm ON cs.id = cm.session_id
GROUP BY cs.id
ORDER BY MAX(cm.timestamp) DESC;
```

Check database size:
```sql
SELECT pg_size_pretty(pg_database_size('adaptive_rag_db'));
```

### Backup and Restore

Backup:
```bash
pg_dump -U yvettegonzalez -h localhost adaptive_rag_db > backup.sql
```

Restore:
```bash
psql -U yvettegonzalez -h localhost adaptive_rag_db < backup.sql
```

## Troubleshooting

1. **Connection refused error**:
   - Ensure PostgreSQL is running
   - Check if port 5432 is available
   - Verify DATABASE_URL is correct

2. **Authentication failed**:
   - Run the setup script again
   - Check pg_hba.conf allows local connections

3. **Database does not exist**:
   - Run `./setup_postgres.sh` to create it
   - Or manually create with: `createdb adaptive_rag_db`

## Production Considerations

For production deployments:

1. Use a managed PostgreSQL service (AWS RDS, Google Cloud SQL, etc.)
2. Enable SSL connections
3. Set up regular backups
4. Monitor database performance
5. Consider connection pooling with pgBouncer for high traffic