from database.schema_extractor import SchemaExtractor


extractor = SchemaExtractor()

schema = extractor.get_schema()

print("\n" + "=" * 60)
print("DATABASE SCHEMA")
print("=" * 60)

print(schema)

extractor.close()