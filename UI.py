from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_core.messages import HumanMessage
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv
from typing import Optional

from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache

# Initialize SQLite cache (creates langchain_cache.db file)
set_llm_cache(SQLiteCache(database_path=".langchain_cache.db"))


# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Database connection function
def get_db_connection():
    """Get database connection with fallback to SQLite if PostgreSQL not available"""
    try:
        # Try PostgreSQL first
        import psycopg2
        return psycopg2.connect(
            host=os.environ.get("PGHOST", "localhost"),
            port=os.environ.get("PGPORT", "5432"),
            database=os.environ.get("PGDATABASE", "incidents"),
            user=os.environ.get("PGUSER", "postgres"),
            password=os.environ.get("PGPASSWORD", "")
        )
    except (ImportError, Exception) as e:
        print(f"PostgreSQL not available, using SQLite: {e}")
        # Fallback to SQLite
        import sqlite3
        conn = sqlite3.connect('incidents.db')
        conn.row_factory = sqlite3.Row
        return conn

def init_database():
    """Initialize the database with required tables"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if we're using PostgreSQL or SQLite
        if hasattr(conn, 'server_version'):  # PostgreSQL
            # Create incident schema if it doesn't exist
            cur.execute("CREATE SCHEMA IF NOT EXISTS incident;")
            # Create hp_incidents table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS incident.hp_incidents (
                    id SERIAL PRIMARY KEY,
                    ticket_id VARCHAR(20) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    department VARCHAR(100) NOT NULL,
                    issue_type VARCHAR(100) NOT NULL,
                    description TEXT NOT NULL,
                    priority VARCHAR(20) DEFAULT 'Medium',
                    status VARCHAR(20) DEFAULT 'Open',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            # Ensure due_date column exists (for legacy tables)
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_schema='incident' AND table_name='hp_incidents'
                    ) THEN
                    END IF;
                END$$;
            """)
        else:  # SQLite
            cur.execute("""
                CREATE TABLE IF NOT EXISTS hp_incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    department TEXT NOT NULL,
                    issue_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    priority TEXT DEFAULT 'Medium',
                    status TEXT DEFAULT 'Open',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        
        # Commit the changes
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Database initialized successfully")
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        print("💡 Run 'python fix_database.py' to fix database structure issues")

# Initialize database on startup
init_database()

@app.route('/process_ticket/', methods=['POST'])
def process_ticket():
    data = request.json
    ticket_text = data.get("text", "")
    if not ticket_text:
        return jsonify({"error": "No ticket text provided"}), 400
    # Generate structured output using LangChain structured LLM
    try:
        # Lazy import to avoid failing app startup if env is missing
        from app.nodes.struc_output import llm_structured  # noqa: WPS433
        result_model = llm_structured.invoke([HumanMessage(content=ticket_text)])
        structured_output = result_model.model_dump()
    except Exception as exc:
        return jsonify({"error": f"Failed to analyze ticket: {str(exc)}"}), 500

    return jsonify({"structured_output": structured_output}), 200

@app.route('/ticket', methods=['POST'])
def create_ticket():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        # Generate a unique ticket ID
        ticket_id = str(uuid.uuid4())[:8].upper()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Print received data for debugging
        print(f"Debug - Received data: {data}")
        print(f"Debug - Generated ticket_id: {ticket_id}")
        print(f"Debug - Current time: {current_time}")
        
        # Get database connection
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if we're using PostgreSQL or SQLite
        if hasattr(conn, 'server_version'):  # PostgreSQL
            cur.execute("""
                INSERT INTO incident.hp_incidents 
                (ticket_id, name, department, issue_type, description, priority, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                ticket_id,
                data.get("name", ""),
                data.get("department", ""),
                data.get("issue_type", ""),
                data.get("description", ""),
                data.get("priority", "Medium"),
                "Open",
                current_time
            ))
        else:  # For SQLite
            print("Using SQLite")
            try:
                # Close the current connection and create a direct SQLite connection
                if conn:
                    conn.close()
                
                import sqlite3
                sqlite_conn = sqlite3.connect('incidents.db')
                sqlite_cur = sqlite_conn.cursor()
                
                # Use direct SQLite connection with minimal parameters
                sqlite_cur.execute(
                    "INSERT INTO incidents (ticket_id, name, department, issue_type, description, priority, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (ticket_id, data.get("name", ""), data.get("department", ""), data.get("issue_type", ""), 
                     data.get("description", ""), data.get("priority", "Medium"), "Open", current_time)
                )
                
                # Commit and close the direct connection
                sqlite_conn.commit()
                sqlite_conn.close()
                
                # Reopen the original connection for consistency
                conn = get_db_connection()
                cur = conn.cursor()
                
            except Exception as e:
                print(f"SQLite execution error: {e}")
                print(f"Error details: {type(e).__name__}")
                import traceback
                print(traceback.format_exc())
                raise
        
        # Commit the transaction
        conn.commit()
        
        # Close database connection
        cur.close()
        conn.close()
        
        return jsonify({
            "ticket_id": ticket_id, 
            "message": "Ticket created successfully and stored in database"
        }), 200
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in create_ticket: {str(e)}")
        print(f"Error details: {error_details}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route('/tickets', methods=['GET'])
def get_tickets():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if we're using PostgreSQL or SQLite
        if hasattr(conn, 'server_version'):  # PostgreSQL
            cur.execute("""
                SELECT ticket_id, status, updated_at
                FROM incident.hp_incidents
                ORDER BY created_at DESC
            """)
        else:  # SQLite
            cur.execute("""
                SELECT ticket_id, status, updated_at
                FROM incidents
                ORDER BY created_at DESC
            """)
        
        tickets = []
        for row in cur.fetchall():
            tickets.append({
                "ticket_id": row[0],
                "status": row[1],
                "updated_at": row[2]
            })
        
        cur.close()
        conn.close()
        
        return jsonify({"tickets": tickets}), 200
        
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route('/ticket/<ticket_id>/status', methods=['GET'])
def get_ticket_status(ticket_id):
    """Get status of a specific ticket (minimal columns)"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if we're using PostgreSQL or SQLite
        if hasattr(conn, 'server_version'):  # PostgreSQL
            cur.execute("""
                SELECT ticket_id, status, updated_at
                FROM incident.hp_incidents
                WHERE ticket_id = %s
            """, (ticket_id,))
        else:  # SQLite
            cur.execute("""
                SELECT ticket_id, status, updated_at
                FROM incidents
                WHERE ticket_id = ?
            """, (ticket_id,))
        
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if row:
            ticket = {
                "ticket_id": row[0],
                "status": row[1],
                "updated_at": row[2]
            }
            return jsonify({"ticket": ticket}), 200
        else:
            return jsonify({"error": "Ticket not found"}), 404
        
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route('/ticket/<ticket_id>/status', methods=['PUT'])
def update_ticket_status(ticket_id):
    """Update status of a specific ticket"""
    data = request.json
    new_status = data.get("status")
    
    if not new_status:
        return jsonify({"error": "No status provided"}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if we're using PostgreSQL or SQLite
        if hasattr(conn, 'server_version'):  # PostgreSQL
            cur.execute("""
                UPDATE incident.hp_incidents
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE ticket_id = %s
            """, (new_status, ticket_id))
        else:  # SQLite
            cur.execute("""
                UPDATE incidents
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE ticket_id = ?
            """, (new_status, ticket_id))
        
        if cur.rowcount == 0:
            cur.close()
            conn.close()
            return jsonify({"error": "Ticket not found"}), 404
        
        # Commit the transaction
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"message": f"Ticket {ticket_id} status updated to {new_status}"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route('/ticket-stats', methods=['GET'])
def get_ticket_stats():
    """Get ticket statistics"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if we're using PostgreSQL or SQLite
        if hasattr(conn, 'server_version'):  # PostgreSQL
            cur.execute("""
                SELECT 
                    COUNT(*) as total_tickets,
                    COUNT(CASE WHEN status = 'Open' THEN 1 END) as open_tickets,
                    COUNT(CASE WHEN status = 'In Progress' THEN 1 END) as in_progress_tickets,
                    COUNT(CASE WHEN status = 'Resolved' THEN 1 END) as resolved_tickets,
                    COUNT(CASE WHEN priority = 'Critical' THEN 1 END) as critical_tickets
                FROM incident.hp_incidents
            """)
        else:  # SQLite
            cur.execute("""
                SELECT 
                    COUNT(*) as total_tickets,
                    COUNT(CASE WHEN status = 'Open' THEN 1 END) as open_tickets,
                    COUNT(CASE WHEN status = 'In Progress' THEN 1 END) as in_progress_tickets,
                    COUNT(CASE WHEN status = 'Resolved' THEN 1 END) as resolved_tickets,
                    COUNT(CASE WHEN priority = 'Critical' THEN 1 END) as critical_tickets
                FROM incidents
            """)
        
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        stats = {
            "total_tickets": row[0],
            "open_tickets": row[1],
            "in_progress_tickets": row[2],
            "resolved_tickets": row[3],
            "critical_tickets": row[4]
        }
        
        return jsonify({"stats": stats}), 200
        
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get("query", "")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Import cache
        from app.utils.cache_utils import response_cache
        
        # Check if response is in cache for non-streaming requests
        use_cache = data.get("use_cache", True)  # Default to using cache
        if use_cache and not data.get("stream", False):
            cached_response = response_cache.get(query)
            if cached_response:
                print("Using cached response")
                return jsonify({"answer": cached_response, "cached": True}), 200
        
        # Use LangGraph pipeline to generate LLM answer
        from app.graph import graph  # noqa: WPS433
        from flask import Response, stream_with_context
        import json
        
        def generate_stream():
            state_in = {"messages": [HumanMessage(content=query)]}
            # Use stream=True for streaming response
            full_response = ""
            for chunk_state in graph.stream(state_in):
                messages = chunk_state.get("messages", [])
                if messages and hasattr(messages[-1], "content"):
                    chunk_text = messages[-1].content
                    if chunk_text:
                        full_response = chunk_text  # Keep track of full response
                        yield f"data: {json.dumps({'chunk': chunk_text})}\n\n"
            
            # Cache the full response when streaming is complete
            if use_cache and full_response:
                response_cache.set(query, full_response)
                
            yield f"data: {json.dumps({'done': True})}\n\n"
        
        # Check if client requested streaming
        if data.get("stream", False):
            return Response(stream_with_context(generate_stream()), 
                           mimetype="text/event-stream")
        else:
            # Non-streaming fallback
            state_in = {"messages": [HumanMessage(content=query)]}
            result_state = graph.invoke(state_in)
            messages = result_state.get("messages", [])
            answer_text = messages[-1].content if messages else ""
            if not answer_text:
                answer_text = "Sorry, I couldn't generate a response right now. Please try again."
            
            # Cache the response
            if use_cache:
                response_cache.set(query, answer_text)
                
            return jsonify({"answer": answer_text, "cached": False}), 200
    except Exception as e:
        return jsonify({"error": f"Chat error: {str(e)}"}), 500

@app.get('/healthz')
def healthz():
    return jsonify({"status": "ok"}), 200

@app.get('/test')
def test():
    return jsonify({"message": "Backend is running!"}), 200

if __name__ == '__main__':
    print("🚀 Starting Flask server...")
    print("📡 Server will be available at: http://127.0.0.1:8000")
    print("🔧 Test endpoint: http://127.0.0.1:8000/test")
    app.run(host='127.0.0.1', port=8000, debug=False, use_reloader=False)