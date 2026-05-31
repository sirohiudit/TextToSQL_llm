from app.text_to_sql_pipeline import TextToSQLPipeline


pipeline = TextToSQLPipeline()


question = """
Which product categories generated the highest revenue?
"""


response = pipeline.run(question)


print("\n" + "=" * 70)
print("QUESTION")
print("=" * 70)
print(response["question"])


print("\n" + "=" * 70)
print("GENERATED SQL")
print("=" * 70)
print(response["generated_sql"])


print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)

result = response["execution_result"]

if result["success"]:

    for row in result["results"]:
        print(row)

else:

    print("ERROR:")
    print(result["error"])


pipeline.close()