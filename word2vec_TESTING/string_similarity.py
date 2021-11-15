# This file requires spaCy and spaCy's en_core_web_lg model

# For download instructions, visit
# https://spacy.io/usage
# and
# https://spacy.io/models

import spacy


def getSimilarity(nlp, string1, string2):
    vec1 = nlp(string1)
    vec2 = nlp(string2)

    similarity = vec1.similarity(vec2)

    print("similarity WITH stopwords")
    print(vec1.text, vec2.text, similarity)

    return similarity

def getSimilarityNoStop(nlp, string1, string2):
    vec1 = nlp(string1)
    vec2 = nlp(string2)

    vec1_no_stop = nlp(' '.join([str(t) for t in vec1 if not t.is_stop]))
    vec2_no_stop = nlp(' '.join([str(t) for t in vec2 if not t.is_stop]))

    similarity_no_stop = vec1_no_stop.similarity(vec2_no_stop)

    print("similarity NO stopwords")
    print(vec1_no_stop.text, vec2_no_stop.text, similarity_no_stop)

    return similarity_no_stop

if __name__ == '__main__':
    nlp = spacy.load("en_core_web_lg")

    words = []
    strings = []
    data = []
    # words = ['test', 'quiz', 'exam', 'practice', 'hardy']
    # strings = ['I went down to the river to pray', 'mathematicians examine rudimentary proofs']
    # data = ['Data Engineer Chicago IL Months Contract', 'Scientist I', 'Data Scientist Programmer',
            # 'Business Analyst Data Scientist Manager',
            # 'Associate Product Development Scientist Nutrition Columbus OH']

    testCases = ['Data Scientist of Bioinformatics', 'Data Scientist of Medicine',
            'Data Scientist of Military']

    for word1 in words:
        for word2 in words:
            getSimilarity(nlp, word1, word2)
            getSimilarityNoStop(nlp, word1, word2)

    for string1 in strings:
        for string2 in strings:
            getSimilarity(nlp, string1, string2)
            getSimilarityNoStop(nlp, string1, string2)

    for data1 in data:
        for data2 in data:
            getSimilarity(nlp, data1, data2)
            getSimilarityNoStop(nlp, data1, data2)

    for case1 in testCases:
        for case2 in testCases:
            getSimilarity(nlp, case1, case2)
            getSimilarityNoStop(nlp, case1, case2)
