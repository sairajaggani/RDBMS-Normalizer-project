import pandas as pd
from itertools import combinations
from collections import defaultdict

class MVDAnalyzer:
    def __init__(self, csv_file):
        self.df = pd.read_csv(csv_file)
        self.columns = list(self.df.columns)
    

    
    def get_functional_dependencies(self):
       
        fds = []
        for col1 in self.columns:
            for col2 in self.columns:
                if col1 != col2:
                   
                    groups = self.df.groupby(col1)[col2].nunique()
                    if all(groups == 1):
                        fds.append((col1, col2))
        return fds
    
    def check_mvd_pattern(self, determinant_cols, dependent_col):

        # Group by determinant columns
        grouped = self.df.groupby(determinant_cols)
        
        # Check each group for MVD pattern
        valid_groups = 0
        total_groups = 0
        
        for name, group in grouped:
            total_groups += 1
            dependent_values = set(group[dependent_col])
            
            other_cols = [col for col in self.columns 
                         if col not in determinant_cols and col != dependent_col]
            
            if not other_cols:
                continue
                
            other_combinations = group[other_cols].drop_duplicates()
            expected_combinations = len(dependent_values) * len(other_combinations)
            actual_combinations = len(group)
            
            tolerance = 0.9
            if actual_combinations >= expected_combinations * tolerance:
                valid_groups += 1
        
        group_threshold = 0.8
        return valid_groups / total_groups >= group_threshold if total_groups > 0 else False

    def find_data_driven_mvds(self):
        #Find MVDs that are supported by actual data patterns.
        valid_mvds = []
        
        fds = self.get_functional_dependencies()
        fd_determinants = set(fd[0] for fd in fds)
        
        for det_size in range(1, len(self.columns) - 1):
            for determinant_cols in combinations(self.columns, det_size):
                determinant_cols = list(determinant_cols)
                remaining_cols = [col for col in self.columns if col not in determinant_cols]
                
                if any(det in fd_determinants for det in determinant_cols):
                    continue
                
                for dependent_col in remaining_cols:
                    if self.check_mvd_pattern(determinant_cols, dependent_col):
                        valid_mvds.append({
                            'determinant': determinant_cols,
                            'dependent': dependent_col
                        })
        
        return valid_mvds

    def perform_4nf_decomposition(self):
        #Perform 4NF decomposition based on discovered MVDs.
        mvds = self.find_data_driven_mvds()
        tables_4nf = []
        
        # Start with the original table
        remaining_cols = set(self.columns)
        
        # Process each MVD
        for mvd in mvds:
            det_cols = set(mvd['determinant'])
            dep_col = mvd['dependent']
            
          
            table_cols = det_cols | {dep_col}
            tables_4nf.append({
                'name': f"table_4nf_{len(tables_4nf) + 1}",
                'columns': list(table_cols),
                'primary_key': list(det_cols) + [dep_col]
            })
            
            remaining_cols -= {dep_col}
        
        
        if remaining_cols:
            tables_4nf.append({
                'name': f"table_4nf_{len(tables_4nf) + 1}",
                'columns': list(remaining_cols),
                'primary_key': list(remaining_cols)  # Simplified assumption
            })
        
        return tables_4nf

    def identify_join_dependencies(self):
        
        join_deps = []
        tables_4nf = self.perform_4nf_decomposition()
        
        # Look for potential circular joins
        for size in range(3, len(tables_4nf) + 1):
            for table_combo in combinations(tables_4nf, size):
                # Check if tables can be joined in a cycle
                common_cols = set.intersection(*[set(t['columns']) for t in table_combo])
                if common_cols:
                    join_deps.append({
                        'tables': table_combo,
                        'common_columns': list(common_cols)
                    })
        
        return join_deps

    def perform_5nf_decomposition(self):
        
        tables_4nf = self.perform_4nf_decomposition()
        join_deps = self.identify_join_dependencies()
        tables_5nf = []

        

        tables_5nf.extend(tables_4nf)
        
        # Further decompose based on join dependencies
        for jd in join_deps:
            for i, table in enumerate(jd['tables']):
                # Create new table for each component of the join dependency
                new_table = {
                    'name': f"table_5nf_{len(tables_5nf) + 1}",
                    'columns': list(set(table['columns']) & 
                                 set(jd['common_columns'])),
                    'primary_key': list(set(table['primary_key']) & 
                                      set(jd['common_columns']))
                }
              #  if new_table['columns'] and new_table not in tables_5nf:
              #      tables_5nf.append(new_table)
        
        return tables_5nf

    def generate_create_table_queries(self, tables):
        
        queries = []
        
        for table in tables:
            columns_sql = []
            for col in table['columns']:
                # Simplified data type inference
                data_type = self._infer_sql_type(self.df[col])
                columns_sql.append(f"{col} {data_type}")
            
            pk_clause = f"PRIMARY KEY ({', '.join(table['primary_key'])})"
            columns_sql.append(pk_clause)
            
            query = f"CREATE TABLE {table['name']} (\n    "
            query += ",\n    ".join(columns_sql)
            query += "\n);"
            queries.append(query)
        
        return queries

    def _infer_sql_type(self, series):
        
        dtype = str(series.dtype)
        if 'int' in dtype:
            return 'INTEGER'
        elif 'float' in dtype:
            return 'DECIMAL'
        elif 'datetime' in dtype:
            return 'TIMESTAMP'
        else:
            max_length = series.astype(str).str.len().max()
            return f'VARCHAR({max_length})'

def analyze_and_print_normalization(csv_file):
   
    analyzer = MVDAnalyzer(csv_file)
    
    print("\nMulti-valued Dependencies:")
    print("=" * 50)
    mvds = analyzer.find_data_driven_mvds()
    for mvd in mvds:
        print(f"{', '.join(mvd['determinant'])} ->> {mvd['dependent']}")
    
    print("\n4NF Decomposition:")
    print("=" * 50)
    tables_4nf = analyzer.perform_4nf_decomposition()
    queries_4nf = analyzer.generate_create_table_queries(tables_4nf)
    for query in queries_4nf:
        print(f"\n{query}")
    
    print("\n5NF Decomposition:")
    print("=" * 50)
    tables_5nf = analyzer.perform_5nf_decomposition()
    queries_5nf = analyzer.generate_create_table_queries(tables_5nf)
    for query in queries_5nf:
        print(f"\n{query}")

if __name__ == "__main__":
    analyze_and_print_normalization('test.csv')
    