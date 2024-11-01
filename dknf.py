import csv
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class FunctionalDependency:
    def __init__(self, determinants, dependents, is_multivalued=False):
        self.determinants = set(determinants)
        self.dependents = set(dependents)
        self.is_multivalued = is_multivalued

    def __repr__(self):
        arrow = "-->>" if self.is_multivalued else "->"
        return f"{self.determinants} {arrow} {self.dependents}"

class DKNFNormalizer:
    def __init__(self):
        self.attributes: Set[str] = set()
        self.functional_dependencies: List[Tuple[Set[str], Set[str]]] = []
        self.domain_constraints: Dict[str, Set[str]] = {}
        self.key_constraints: List[Set[str]] = []
        self.data: List[Dict[str, str]] = []
        self.table_name: str = ""

    def load_data_from_csv(self, csv_path: str) -> None:
        """Load data from CSV file and extract attributes."""
        self.table_name = csv_path.split('.')[0].capitalize()
        with open(csv_path, 'r') as file:
            csv_reader = csv.DictReader(file)
            self.data = list(csv_reader)
            self.attributes.update(csv_reader.fieldnames)

    def load_constraints_from_file(self, constraints_path: str) -> None:
        """Load constraints from a text file."""
        with open(constraints_path, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if line.startswith('FD:'):
                    fd_parts = line[3:].strip().split('->')
                    determinant = set(fd_parts[0].strip().split(','))
                    dependent = set(fd_parts[1].strip().split(','))
                    self.functional_dependencies.append((determinant, dependent))

                elif line.startswith('KEY:'):
                    key_attrs = set(line[4:].strip().split(','))
                    self.key_constraints.append(key_attrs)

                elif line.startswith('DOMAIN:'):
                    domain_parts = line[7:].strip().split(':')
                    attribute = domain_parts[0].strip()
                    values = set(domain_parts[1].strip().split(','))
                    self.domain_constraints[attribute] = values

    def _compute_closure(self, attributes: Set[str], fds: List[Tuple[Set[str], Set[str]]]) -> Set[str]:
        """Compute the attribute closure under given functional dependencies."""
        closure = attributes.copy()
        changed = True
        while changed:
            changed = False
            for det, dep in fds:
                if det.issubset(closure) and not dep.issubset(closure):
                    closure.update(dep)
                    changed = True
        return closure

    def _is_superkey(self, attributes: Set[str], relation_attrs: Set[str]) -> bool:
        """Check if attributes form a superkey for the relation."""
        closure = self._compute_closure(attributes, self.functional_dependencies)
        return relation_attrs.issubset(closure)

    def _decompose_to_dknf(self) -> List[Dict]:
        """Perform DKNF decomposition."""
        print("\nDKNF Decomposition Process:")
        print("=" * 50)
        
        decomposed_relations = []
        processed_attrs = set()

        # Step 1: Create relations from key constraints
        for key in self.key_constraints:
            closure = self._compute_closure(key, self.functional_dependencies)
            relation = {
                'name': f"{self.table_name}_Key_{len(decomposed_relations) + 1}",
                'attributes': closure,
                'key': key
            }
            decomposed_relations.append(relation)
            processed_attrs.update(closure)

            print(f"\nRelation {len(decomposed_relations)}:")
            print(f"Name: {relation['name']}")
            print(f"Attributes: {', '.join(sorted(closure))}")
            print(f"Key: {', '.join(sorted(key))}")

        # Step 2: Handle remaining attributes (those not covered by any key)
        remaining_attrs = self.attributes - processed_attrs
        if remaining_attrs:
            relation = {
                'name': f"{self.table_name}_Remainder",
                'attributes': remaining_attrs,
                'key': remaining_attrs  # Ensure that each attribute can act as its own key
            }
            decomposed_relations.append(relation)

            print(f"\nRelation {len(decomposed_relations)} (Remaining Attributes):")
            print(f"Name: {relation['name']}")
            print(f"Attributes: {', '.join(sorted(remaining_attrs))}")
            print("Key: Each attribute is its own key")

        return decomposed_relations



    def generate_sql_queries(self, relations: List[Dict]) -> List[str]:
        """Generate SQL queries for the DKNF relations."""
        sql_queries = []

        print("\nGenerated SQL Queries:")
        print("=" * 50)

        for relation in relations:
            # CREATE TABLE statement
            create_query = f"CREATE TABLE {relation['name']} (\n"
            columns = [f"    {attr} VARCHAR(255)" for attr in sorted(relation['attributes'])]
            columns.append(f"    PRIMARY KEY ({', '.join(sorted(relation['key']))})")
            create_query += ',\n'.join(columns) + "\n);"
            sql_queries.append(create_query)

            # Print the query
            print(create_query)

        return sql_queries

    def normalize(self):
        """Perform the complete DKNF normalization process."""
        # Decompose to DKNF
        relations = self._decompose_to_dknf()

        # Generate SQL queries
        self.generate_sql_queries(relations)

def main():
    # Run the normalization process
    normalizer = DKNFNormalizer()
    normalizer.load_data_from_csv('Orders.csv')
    normalizer.load_constraints_from_file('constraints.txt')
    normalizer.normalize()

if __name__ == "__main__":
    main()
