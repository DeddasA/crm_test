import spacy
nlp = spacy.load("pt_core_news_sm")
user_input ="São paulo na China"
doc = nlp(user_input)

for ent in doc.ents:
    print(ent)
    if ent.label_ == "LOC":
        print('yes')

    else:
        print("no")



for token in doc:
    print(token.ent_type_)
