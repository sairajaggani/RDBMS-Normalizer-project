import pandas as pd
import os
import re
from collections import defaultdict
from itertools import combinations


class FunctionalDependency:
    def __init__(self, determinants, dependents, is_multivalued=False):
        self.determinants = set(determinants)
        self.dependents = set(dependents)
        self.is_multivalued = is_multivalued

    def __str__(self):
        det_str = ','.join(sorted(self.determinants))
        dep_str = ','.join(sorted(self.dependents))
        arrow = '-->>' if self.is_multivalued else '->'
        return f"{{{det_str}}} {arrow} {{{dep_str}}}"

def parse_fd_file(file_path):
   
    fds = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                    
                # Check if it's a multivalued dependency
                is_multivalued = '-->>' in line
                
                # Split the line into determinants and dependents
                parts = line.split('-->>' if is_multivalued else '->')
                if len(parts) != 2:
                    continue
                
                # Parse determinants
                determinants_str = parts[0].strip('{}')
                determinants = [d.strip() for d in determinants_str.split(',')]
                
                # Parse dependents
                dependents_str = parts[1].strip('{}')
                dependents = [d.strip() for d in dependents_str.split(',')]
                
                fds.append(FunctionalDependency(determinants, dependents, is_multivalued))
                
        return fds
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []

def print_mvds(fds):
    print("Multivalued Dependencies:")
    for fd in fds:
        if fd.is_multivalued:
            print(f"MVD {fd.determinants} -->> {fd.dependents}")

def read_csv(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None

def normalize_to_1nf(df, primary_keys):
   
    #Normalizes the DataFrame to 1NF by splitting multivalued attributes.
   # Creates separate relations for multivalued attributes.
   # Returns a list of SQL queries and information about created tables.
    
    tables_info = []
    queries = []
    base_table_name = "MainTable"

    # Create main table query
    main_table_query = f"CREATE TABLE {base_table_name} (\n"
    for col in df.columns:
        sql_type = 'VARCHAR(255)' if df[col].dtype == object else 'INT'
        main_table_query += f"  {col} {sql_type},\n"
    main_table_query += f"  PRIMARY KEY ({', '.join(primary_keys)})\n);"
    queries.append(("MainTable", main_table_query))
    tables_info.append({
        "name": base_table_name,
        "columns": list(df.columns),
        "primary_keys": primary_keys
    })

    # Handle multivalued attributes - create separate relations with all primary keys
    for col in df.columns:
        if df[col].dtype == object and df[col].str.contains(',').any():
            table_name = f"{col}_Table"
            query = f"CREATE TABLE {table_name} (\n"
            
            # Include all primary keys from base relation
            for pk in primary_keys:
                sql_type = 'VARCHAR(255)' if df[pk].dtype == object else 'INT'
                query += f"  {pk} {sql_type},\n"
            
            # Add the multivalued attribute
            query += f"  {col} VARCHAR(255),\n"
            
            # Composite primary key of all original primary keys plus the multivalued attribute
            all_keys = primary_keys + [col]
            query += f"  PRIMARY KEY ({', '.join(all_keys)})\n);"
            
            queries.append((table_name, query))
            tables_info.append({
                "name": table_name,
                "columns": primary_keys + [col],
                "primary_keys": all_keys
            })

    return queries, tables_info

def check_partial_dependencies(table_info, fds):
    
    #Check for partial dependencies in a table and return tables that need to be decomposed.
    
    primary_key_set = set(table_info["primary_keys"])
    decomposed_tables = {}
    
    for fd in fds:
        if fd.is_multivalued:
            continue
        
        # Check if this FD affects this table
        if not (fd.determinants.issubset(set(table_info["columns"])) and 
                fd.dependents.issubset(set(table_info["columns"]))):
            continue
            
        # Check if determinant is a proper subset of primary key
        if fd.determinants.issubset(primary_key_set) and fd.determinants != primary_key_set:
            table_name = f"{table_info['name']}_Decomposed_{len(decomposed_tables) + 1}"
            decomposed_tables[table_name] = {
                'determinants': fd.determinants,
                'dependents': fd.dependents
            }
    
    return decomposed_tables

def generate_2nf_queries(tables_info, fds):
    #Generate SQL queries for 2NF tables based on 1NF tables.
    queries = []
    final_tables_info = []
    
    for table_info in tables_info:
        decomposed_tables = check_partial_dependencies(table_info, fds)
        
        if not decomposed_tables:
            # If no partial dependencies, keep the original table
            queries.append((table_info["name"], f"-- Table {table_info['name']} is already in 2NF\n" +
                          f"CREATE TABLE {table_info['name']} (\n" +
                          "\n".join(f"  {col} VARCHAR(255)," for col in table_info["columns"]) +
                          f"\n  PRIMARY KEY ({', '.join(table_info['primary_keys'])})\n);"))
            final_tables_info.append(table_info)
        else:
            # Create decomposed tables for 2NF
            used_attributes = set()
            
            # Create tables for each partial dependency
            for table_name, table_info_2nf in decomposed_tables.items():
                query = f"CREATE TABLE {table_name} (\n"
                columns = list(table_info_2nf['determinants']) + list(table_info_2nf['dependents'])
                
                for col in columns:
                    query += f"  {col} VARCHAR(255),\n"
                    used_attributes.add(col)
                
                query += f"  PRIMARY KEY ({', '.join(table_info_2nf['determinants'])})\n);"
                queries.append((table_name, query))
                final_tables_info.append({
                    "name": table_name,
                    "columns": columns,
                    "primary_keys": list(table_info_2nf['determinants'])
                })
            
            # Create table with remaining attributes if any
            remaining_attrs = set(table_info["columns"]) - used_attributes
            if remaining_attrs:
                remaining_table_name = f"{table_info['name']}_Remaining"
                query = f"CREATE TABLE {remaining_table_name} (\n"
                for col in remaining_attrs:
                    query += f"  {col} VARCHAR(255),\n"
                query += f"  PRIMARY KEY ({', '.join(table_info['primary_keys'])})\n);"
                queries.append((remaining_table_name, query))
                final_tables_info.append({
                    "name": remaining_table_name,
                    "columns": list(remaining_attrs),
                    "primary_keys": table_info['primary_keys']
                })
    
    return queries, final_tables_info

def find_transitive_dependencies(table_info, fds):
    
   # Find transitive dependencies in a table. A->B and B->C implies A->C is transitive if A is a key.

    transitive_deps = {}
    primary_key_set = set(table_info["primary_keys"])
    columns = set(table_info["columns"])
    
    # Create a dependency graph
    dep_graph = defaultdict(set)
    for fd in fds:
        if fd.is_multivalued:
            continue
        if not (fd.determinants.issubset(columns) and fd.dependents.issubset(columns)):
            continue
        for det in fd.determinants:
            for dep in fd.dependents:
                dep_graph[det].add(dep)
    
    # Find transitive dependencies
    for fd1 in fds:
        if fd1.is_multivalued:
            continue
        if not (fd1.determinants.issubset(columns) and fd1.dependents.issubset(columns)):
            continue
        
        # Check if this FD starts from a non-key attribute
        if not fd1.determinants.issubset(primary_key_set):
            for fd2 in fds:
                if fd2.is_multivalued:
                    continue
                if not (fd2.determinants.issubset(columns) and fd2.dependents.issubset(columns)):
                    continue
                
                # If fd1: A->B and fd2: B->C, then we have a transitive dependency
                if fd2.determinants.issubset(fd1.dependents):
                    table_name = f"{table_info['name']}_Trans_{len(transitive_deps) + 1}"
                    transitive_deps[table_name] = {
                        'determinants': fd1.dependents,
                        'dependents': fd2.dependents
                    }
    
    return transitive_deps

def generate_3nf_queries(tables_info, fds):
    #Generate SQL queries for 3NF tables based on 2NF tables.
    queries = []
    final_tables_info = []
    
    for table_info in tables_info:
        transitive_deps = find_transitive_dependencies(table_info, fds)
        
        if not transitive_deps:
            # If no transitive dependencies, keep the original table
            queries.append((table_info["name"], f"-- Table {table_info['name']} is already in 3NF\n" +
                          f"CREATE TABLE {table_info['name']} (\n" +
                          "\n".join(f"  {col} VARCHAR(255)," for col in table_info["columns"]) +
                          f"\n  PRIMARY KEY ({', '.join(table_info['primary_keys'])})\n);"))
            final_tables_info.append(table_info)
        else:
            # Create decomposed tables for 3NF
            used_attributes = set()
            
            # Create tables for each transitive dependency
            for table_name, table_info_3nf in transitive_deps.items():
                query = f"CREATE TABLE {table_name} (\n"
                columns = list(table_info_3nf['determinants']) + list(table_info_3nf['dependents'])
                
                for col in columns:
                    query += f"  {col} VARCHAR(255),\n"
                    used_attributes.add(col)
                
                query += f"  PRIMARY KEY ({', '.join(table_info_3nf['determinants'])})"
                
                # Add foreign key if the determinant references another table
                for other_table in final_tables_info:
                    if table_info_3nf['determinants'].issubset(set(other_table['columns'])):
                        query += f",\n  FOREIGN KEY ({', '.join(table_info_3nf['determinants'])}) " + \
                                f"REFERENCES {other_table['name']}({', '.join(table_info_3nf['determinants'])})"
                
                query += "\n);"
                queries.append((table_name, query))
                final_tables_info.append({
                    "name": table_name,
                    "columns": columns,
                    "primary_keys": list(table_info_3nf['determinants'])
                })
            
            # Create table with remaining attributes
            remaining_attrs = set(table_info["columns"]) - used_attributes
            if remaining_attrs:
                remaining_table_name = f"{table_info['name']}_Base"
                query = f"CREATE TABLE {remaining_table_name} (\n"
                for col in remaining_attrs:
                    query += f"  {col} VARCHAR(255),\n"
                query += f"  PRIMARY KEY ({', '.join(table_info['primary_keys'])})\n);"
                queries.append((remaining_table_name, query))
                final_tables_info.append({
                    "name": remaining_table_name,
                    "columns": list(remaining_attrs),
                    "primary_keys": table_info['primary_keys']
                })
    
    return queries, final_tables_info



def compute_closure(attributes, fds):
   #Compute the attribute closure for a given set of attributes under given FDs
    closure = set(attributes)
    changed = True
    
    while changed:
        changed = False
        for fd in fds:
            if not fd.is_multivalued and fd.determinants.issubset(closure):
                new_attrs = fd.dependents - closure
                if new_attrs:
                    closure.update(new_attrs)
                    changed = True
                    
    return closure

def is_superkey(attributes, all_attributes, fds):
   
    closure = compute_closure(attributes, fds)
    return all_attributes.issubset(closure)

def find_bcnf_violations(table_info, fds):
   
    # Find BCNF violations in a table. A violation occurs when a determinant is not a superkey.
   
    violations = {}
    columns = set(table_info["columns"])
    
    for fd in fds:
        if fd.is_multivalued:
            continue
            
        # Skip FDs that don't apply to this table
        if not (fd.determinants.issubset(columns) and fd.dependents.issubset(columns)):
            continue
        
        # Check if determinant is a superkey
        if not is_superkey(fd.determinants, columns, fds):
            # This is a BCNF violation
            table_name = f"{table_info['name']}_BCNF_{len(violations) + 1}"
            violations[table_name] = {
                'determinants': fd.determinants,
                'dependents': fd.dependents - fd.determinants  # Remove determinants from dependents
            }
    
    return violations

def generate_bcnf_queries(tables_info, fds):
    #Generate SQL queries for BCNF tables based on 3NF tables.
    queries = []
    final_tables_info = []
    
    for table_info in tables_info:
        bcnf_violations = find_bcnf_violations(table_info, fds)
        
        if not bcnf_violations:
            # If no BCNF violations, keep the original table
            queries.append((table_info["name"], f"-- Table {table_info['name']} is already in BCNF\n" +
                          f"CREATE TABLE {table_info['name']} (\n" +
                          "\n".join(f"  {col} VARCHAR(255)," for col in table_info["columns"]) +
                          f"\n  PRIMARY KEY ({', '.join(table_info['primary_keys'])})\n);"))
            final_tables_info.append(table_info)
        else:
            # Create decomposed tables for BCNF
            used_attributes = set()
            
            # Create tables for each BCNF violation
            for table_name, violation_info in bcnf_violations.items():
                # Combine determinants and dependents for all columns
                all_columns = list(violation_info['determinants'].union(violation_info['dependents']))
                
                query = f"CREATE TABLE {table_name} (\n"
                
                # Add columns
                for col in all_columns:
                    query += f"  {col} VARCHAR(255),\n"
                    used_attributes.add(col)
                
                # Add primary key
                query += f"  PRIMARY KEY ({', '.join(violation_info['determinants'])})"
                
                # Add foreign key constraints if applicable
                for other_table in final_tables_info:
                    if violation_info['determinants'].issubset(set(other_table['columns'])):
                        query += f",\n  FOREIGN KEY ({', '.join(violation_info['determinants'])}) " + \
                                f"REFERENCES {other_table['name']}({', '.join(violation_info['determinants'])})"
                
                query += "\n);"
                queries.append((table_name, query))
                
                final_tables_info.append({
                    "name": table_name,
                    "columns": all_columns,
                    "primary_keys": list(violation_info['determinants'])
                })
            
            # Create table with remaining attributes
            remaining_attrs = set(table_info["columns"]) - used_attributes
            if remaining_attrs:
                # Must include any attributes needed for foreign keys
                for violation_info in bcnf_violations.values():
                    remaining_attrs.update(violation_info['determinants'])
                
                remaining_table_name = f"{table_info['name']}_Base"
                query = f"CREATE TABLE {remaining_table_name} (\n"
                for col in remaining_attrs:
                    query += f"  {col} VARCHAR(255),\n"
                query += f"  PRIMARY KEY ({', '.join(table_info['primary_keys'])})\n);"
                queries.append((remaining_table_name, query))
                
                final_tables_info.append({
                    "name": remaining_table_name,
                    "columns": list(remaining_attrs),
                    "primary_keys": table_info['primary_keys']
                })
    
    return queries, final_tables_info

 #  autonomously identify multi-valued dependencies WITHOUT relying on user-provided MVD data. 

def validate_mvd(table_info, data_df, mvd):
   
   # Validate if an MVD X -->> Y holds in the data.
    # For X -->> Y, if two tuples agree on X, their Y values must be independent of Z (remaining attributes).
   
    if data_df.empty:
        return False
        
    # Get remaining attributes (Z)
    all_attrs = set(table_info["columns"])
    remaining_attrs = all_attrs - mvd.determinants - mvd.dependents
    
    # Group by determinant values
    determinant_cols = list(mvd.determinants)
    grouped = data_df.groupby(determinant_cols)
    
    for _, group in grouped:
        if len(group) <= 1:
            continue
            
        # Get unique Y and Z values
        y_values = set(tuple(row) for row in group[list(mvd.dependents)].values)
        z_values = set(tuple(row) for row in group[list(remaining_attrs)].values)
        
        # For MVD to hold, all combinations of Y and Z values should exist
        expected_count = len(y_values) * len(z_values)
        actual_count = len(group)
        
        if actual_count != expected_count:
            return False

    
    return True

def find_4nf_violations(table_info, data_df, fds):
    
    #Find 4NF violations in a table.
  
    violations = {}
    columns = set(table_info["columns"])
    
    for fd in fds:
        if not fd.is_multivalued:
            continue
            
        # Skip MVDs that don't apply to this table
        if not (fd.determinants.issubset(columns) and fd.dependents.issubset(columns)):
            continue
            
        # Validate MVD against actual data
        if not validate_mvd(table_info, data_df, fd):
            continue
        
        # Check if determinant is a superkey
        if not is_superkey(fd.determinants, columns, fds):
            # Check if dependent is not a subset of determinant (non-trivial)
            if not fd.dependents.issubset(fd.determinants):
                # This is a 4NF violation
                table_name = f"{table_info['name']}_4NF_{len(violations) + 1}"
                violations[table_name] = {
                    'determinants': fd.determinants,
                    'dependents': fd.dependents - fd.determinants
                }
    
    return violations

def generate_4nf_queries(tables_info, fds, data_df):
    
   # Generate SQL queries for 4NF tables based on BCNF tables.
  
    
    queries = []
    final_tables_info = []
    
    for table_info in tables_info:
        mvd_violations = find_4nf_violations(table_info, data_df, fds)
        

        
        if not mvd_violations:
            # If no 4NF violations, keep the original table
            queries.append((table_info["name"], f"-- Table {table_info['name']} is already in 4NF\n" +
                          f"CREATE TABLE {table_info['name']} (\n" +
                          "\n".join(f"  {col} VARCHAR(255)," for col in table_info["columns"]) +
                          f"\n  PRIMARY KEY ({', '.join(table_info['primary_keys'])})\n);"))
            final_tables_info.append(table_info)
        else:
            # Create decomposed tables for 4NF
            used_attributes = set()
            
            # Create tables for each MVD violation
            for table_name, violation_info in mvd_violations.items():
                # Combine determinants and dependents for all columns
                all_columns = list(violation_info['determinants'].union(violation_info['dependents']))
                
                query = f"CREATE TABLE {table_name} (\n"
                
                # Add columns
                for col in all_columns:
                    query += f"  {col} VARCHAR(255),\n"
                    used_attributes.add(col)
                
                # Add primary key
                query += f"  PRIMARY KEY ({', '.join(violation_info['determinants'])})"
                
                # Add foreign key constraints if applicable
                for other_table in final_tables_info:
                    if violation_info['determinants'].issubset(set(other_table['columns'])):
                        query += f",\n  FOREIGN KEY ({', '.join(violation_info['determinants'])}) " + \
                                f"REFERENCES {other_table['name']}({', '.join(violation_info['determinants'])})"
                
                query += "\n);"
                queries.append((table_name, query))
                
                final_tables_info.append({
                    "name": table_name,
                    "columns": all_columns,
                    "primary_keys": list(violation_info['determinants'])
                })
            
            # Create table with remaining attributes
            remaining_attrs = set(table_info["columns"]) - used_attributes
            if remaining_attrs:
                # Must include any attributes needed for foreign keys
                for violation_info in mvd_violations.values():
                    remaining_attrs.update(violation_info['determinants'])
                
                remaining_table_name = f"{table_info['name']}_Base"
                query = f"CREATE TABLE {remaining_table_name} (\n"
                for col in remaining_attrs:
                    query += f"  {col} VARCHAR(255),\n"
                query += f"  PRIMARY KEY ({', '.join(table_info['primary_keys'])})\n);"
                queries.append((remaining_table_name, query))
                
                final_tables_info.append({
                    "name": remaining_table_name,
                    "columns": list(remaining_attrs),
                    "primary_keys": table_info['primary_keys']
                })
    
    return queries, final_tables_info

def is_lossless_join(table_info, decomposition, data_df):
   
    # Check if a decomposition has lossless join property.
    
   
    if not decomposition:
        return False
        
    # Project the data into decomposed relations
    projected_dfs = []
    for rel_attrs in decomposition:
        proj_df = data_df[list(rel_attrs)].drop_duplicates()
        projected_dfs.append(proj_df)
    
    # Perform natural join of all projections
    result_df = projected_dfs[0]
    for df in projected_dfs[1:]:
        common_cols = list(set(result_df.columns) & set(df.columns))
        if not common_cols:  # No common attributes for natural join
            return False
        result_df = result_df.merge(df, on=common_cols, how='inner')
    
    # Compare with original relation
    original_df = data_df[list(set().union(*decomposition))].drop_duplicates()
    return len(result_df) == len(original_df)

def find_join_dependencies(table_info, data_df):
   
    #Find join dependencies in a table that violate 5NF.
    #A join dependency exists when a table can be losslessly decomposed into smaller projections.
    
   
    join_deps = {}
    columns = set(table_info["columns"])
    n = len(columns)
    
    # Check all possible decompositions into 3 or more projections
    # Starting with smallest projections first
    for size in range(2, n-1):
        for proj1 in combinations(columns, size):
            proj1 = set(proj1)
            remaining = columns - proj1
            
            for size2 in range(2, len(remaining)):
                for proj2 in combinations(remaining, size2):
                    proj2 = set(proj2)
                    proj3 = remaining - proj2
                    
                    if len(proj3) < 2:  # Each projection should have at least 2 attributes
                        continue
                    
                    decomposition = [proj1, proj2, proj3]
                    
                    # Check if this decomposition is lossless
                    if is_lossless_join(table_info, decomposition, data_df):
                        # Found a join dependency
                        table_name = f"{table_info['name']}_5NF_{len(join_deps) + 1}"
                        join_deps[table_name] = decomposition
    
    return join_deps

def generate_5nf_queries(tables_info, fds, data_df):
    
    
    # Generate SQL queries for 5NF tables based on 4NF tables.
    
    #Args:
    #    tables_info: List of dictionaries containing table metadata
    #    fds: List of FunctionalDependency objects
    #    data_df: DataFrame containing the actual data
    
    queries = []
    final_tables_info = []
    
    for table_info in tables_info:
        join_deps = find_join_dependencies(table_info, data_df)
        
        if not join_deps:
            # If no join dependencies found, table is already in 5NF
            queries.append((table_info["name"], f"-- Table {table_info['name']} is already in 5NF\n" +
                          f"CREATE TABLE {table_info['name']} (\n" +
                          "\n".join(f"  {col} VARCHAR(255)," for col in table_info["columns"]) +
                          f"\n  PRIMARY KEY ({', '.join(table_info['primary_keys'])})\n);"))
            final_tables_info.append(table_info)
        else:
            # Create decomposed tables for each join dependency
            for table_name, decomposition in join_deps.items():
                for i, projection in enumerate(decomposition, 1):
                    proj_table_name = f"{table_name}_Proj_{i}"
                    
                    # Determine primary key for this projection
                    # Use the original primary keys that are part of this projection
                    proj_pkeys = [pk for pk in table_info["primary_keys"] if pk in projection]
                    if not proj_pkeys:  # If no primary keys in projection, use all attributes
                        proj_pkeys = list(projection)
                    
                    query = f"CREATE TABLE {proj_table_name} (\n"
                    
                    # Add columns
                    for col in projection:
                        query += f"  {col} VARCHAR(255),\n"
                    
                    # Add primary key
                    query += f"  PRIMARY KEY ({', '.join(proj_pkeys)})"
                    
                    # Add foreign key constraints if applicable
                    for other_table in final_tables_info:
                        common_keys = set(proj_pkeys) & set(other_table['primary_keys'])
                        if common_keys:
                            query += f",\n  FOREIGN KEY ({', '.join(common_keys)}) " + \
                                    f"REFERENCES {other_table['name']}({', '.join(common_keys)})"
                    
                    query += "\n);"
                    queries.append((proj_table_name, query))
                    
                    final_tables_info.append({
                        "name": proj_table_name,
                        "columns": list(projection),
                        "primary_keys": proj_pkeys
                    })
    
    return queries, final_tables_info

def main():
    # Input: CSV file path and primary keys
    primary_keys = input("Enter the primary keys (comma-separated): ").strip().split(',')

    # Read functional dependencies
    print("\nReading functional dependencies...")
    fds = parse_fd_file('FunctionalDependencies.txt')

    # Read CSV
    print("\nReading CSV file...")
    df = pd.read_csv('MainData.csv')
    if df is None:
        return

    # User chooses the highest normal form
    print("\nChoose the highest Normal Form to reach:")
    print("1. 1NF")
    print("2. 2NF")
    print("3. 3NF")
    print("4. BCNF")
    print("5. 4NF")
    print("6. 5NF")

    try:
        target_nf = int(input("Enter your choice (1-6): "))
        if target_nf < 1 or target_nf > 6:
            raise ValueError("Invalid choice. Please select a number between 1 and 6.")
    except ValueError as e:
        print(f"Error: {e}")
        return




    queries_1nf, tables_info_1nf = normalize_to_1nf(df, primary_keys)
    queries_2nf, tables_info_2nf = generate_2nf_queries(tables_info_1nf, fds)
    queries_3nf, tables_info_3nf = generate_3nf_queries(tables_info_2nf, fds)
    queries_bcnf, tables_info_bcnf = generate_bcnf_queries(tables_info_3nf, fds)
    queries_4nf, final_tables = generate_4nf_queries(tables_info_bcnf, fds,df)
    queries_5nf, final_tables_5nf = generate_5nf_queries(final_tables, fds,df)

    # Step 1: Generate 1NF queries and get table information
    if target_nf == 1:
        print("\n-- Tables in 1NF --")
        save_queries_to_file(queries_1nf, "Output.sql")
        for table_name, query in queries_1nf:
            print(f"\n{query}")

    # Step 2: Generate 2NF queries based on 1NF tables
    if target_nf == 2:
        print("\n-- Tables in 2NF --")
        save_queries_to_file(queries_2nf, "Output.sql")
        for table_name, query in queries_2nf:
            print(f"\n{query}")

    # Step 3: Generate 3NF queries based on 2NF tables
    if target_nf == 3:
        print("\n-- Tables in 3NF --")
        save_queries_to_file(queries_3nf, "Output.sql")
        for table_name, query in queries_3nf:
            print(f"\n{query}")

    # Step 4: Generate BCNF queries based on 3NF tables
    if target_nf == 4:
        print("\n-- Tables in BCNF --")
        save_queries_to_file(queries_bcnf, "Output.sql")
        for table_name, query in queries_bcnf:
            print(f"\n{query}")
    if target_nf ==5:
    # Step 5: Generate 4NF queries based on BCNF tables
        print_mvds(fds)
        print("\n-- Tables in 4NF --")
        save_queries_to_file(queries_4nf, "Output.sql")
        for table_name, query in queries_4nf:
            print(f"\n{query}")
    # Step 6: Generate 5NF queries based on 4NF tables
    if target_nf == 6:
       print("\n-- Tables in 5NF --")
       save_queries_to_file(queries_5nf, "Output.sql")
       for table_name, query in queries_5nf:
            print(f"\n{query}")



def save_queries_to_file(queries, filename):
    """Saves the provided queries to a specified SQL file."""
    try:
        with open(filename, 'w') as file:
            for table_name, query in queries:
                file.write(f"-- Query for {table_name}\n")
                file.write(f"{query};\n\n")
        print(f"Queries saved to {filename}.")
    except Exception as e:
        print(f"Error saving queries to file: {e}")


if __name__ == "__main__":
    main()
