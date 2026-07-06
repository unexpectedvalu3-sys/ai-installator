import sqlite3, json, os

DB_PATH = os.path.expanduser('~/.n8n/database.sqlite')
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Dernière exécution de WF2
cur.execute("""
    SELECT id, "workflowId", status, data
    FROM execution_entity
    WHERE "workflowId" = 'CQcPR4kIgxRoidGY'
    ORDER BY "startedAt" DESC LIMIT 1
""")
row = cur.fetchone()
conn.close()

if row:
    print(f"Exec ID: {row[0]}, status: {row[2]}")
    data = json.loads(row[3]) if row[3] else {}
    result = data.get('resultData', {})

    # Erreur principale
    error = result.get('error', {})
    if error:
        print(f"Error: {error.get('message', '')}")
        print(f"Node: {error.get('node', {}).get('name', '')}")
        print(f"Stack: {str(error.get('stack', ''))[:200]}")

    # Erreurs par node
    run_data = result.get('runData', {})
    for node_name, runs in run_data.items():
        for run in runs:
            if run.get('error'):
                e = run['error']
                print(f"\nNode '{node_name}': {e.get('message', '')} [{e.get('name', '')}]")
                print(f"  Description: {str(e.get('description', ''))[:200]}")
