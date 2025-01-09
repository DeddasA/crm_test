from openai import OpenAI

client = OpenAI(api_key=
'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')

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a haiku about recursion in programming."
        }
    ]
)

print(completion.choices[0].message)