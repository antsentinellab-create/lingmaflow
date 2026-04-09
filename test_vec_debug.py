#!/usr/bin/env python3
import sqlite3, struct, sqlite_vec

conn = sqlite3.connect('repo-index/codebase.db')
sqlite_vec.load(conn)

# Check if there are any vectors in the table
count = conn.execute('SELECT COUNT(*) FROM vec_nodes').fetchone()[0]
print(f'Vector count: {count}')

if count > 0:
    # Get one vector and try to query with it
    row = conn.execute('SELECT node_id, embedding FROM vec_nodes LIMIT 1').fetchone()
    if row:
        node_id, blob = row
        print(f'Testing with node: {node_id}, Blob length: {len(blob)}')
        
        try:
            res = conn.execute('SELECT node_id, vec_distance_cosine(embedding, ?) as dist FROM vec_nodes ORDER BY dist ASC LIMIT 5', [blob]).fetchall()
            print(f'Results: {res}')
        except Exception as e:
            print(f'Error: {e}')
else:
    print('No vectors in database. Inserting a test vector...')
    test_blob = struct.pack('1536f', *[0.1]*1536)
    conn.execute('INSERT INTO vec_nodes(node_id, embedding) VALUES (?, ?)', ['test_node', test_blob])
    conn.commit()
    
    # Now try to query
    try:
        res = conn.execute('SELECT node_id, vec_distance_cosine(embedding, ?) as dist FROM vec_nodes ORDER BY dist ASC LIMIT 5', [test_blob]).fetchall()
        print(f'Results: {res}')
    except Exception as e:
        print(f'Error: {e}')

conn.close()
