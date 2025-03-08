#NLP Concept / Application


#Concept 1: Word Vector Similarity: Utilize pre-trained word vectors to identify similar phrases or terms related to ESG targets.
##    Similar Term Identification: Use word vectors to identify terms similar to key ESG-related words such as "sustainability", "carbon footprint", or "renewable energy" to expand the vocabulary for goal identification.
##    Synonym Detection: Detect synonyms of terms like "target", "goal", or "objective" to capture variations in how ESG goals may be expressed.
##    Context Expansion: Identify words or phrases semantically related to temporal expressions like "by 2025" or "from 2025" to capture different formulations of future targets.
##    Domain-Specific Term Recognition: Utilize word vectors to recognize domain-specific ESG terms that may not be present in a standard lexicon, such as "net-zero emissions" or "environmental stewardship".
##    Comparison of Targets: Compare word vectors associated with terms representing different ESG targets to identify similarities or differences between goals across different sections of the report.

#Concept 2: Entity Linking: Link recognized entities to external knowledge bases or ontologies to gather additional information about ESG-related concepts.

##    External Data Enrichment: Link recognized entities related to ESG goals (e.g., "carbon emissions", "renewable energy sources") to external databases or ontologies to gather additional context, such as historical performance metrics or industry benchmarks.
##    Standardization of Terms: Link recognized entities to standardized vocabularies or taxonomies within the ESG domain to ensure consistency and interoperability with external data sources or reporting frameworks.#
##    Identification of Stakeholders: Link recognized entities representing stakeholders (e.g., "investors", "community members") to external sources to understand their influence on ESG goals and targets.
##    Company-Specific Metrics: Link recognized entities related to company-specific metrics (e.g., "revenue", "market share") to internal databases or performance reports to contextualize ESG goals within broader business objectives.
##    Regulatory Compliance Check: Link recognized entities related to regulatory bodies or compliance standards (e.g., "SEC", "GRI Standards") to relevant regulations or guidelines to ensure alignment of ESG goals with legal requirements.

#Concept 3: Contextual Embeddings:
##
##    Goal Context Identification: Use contextual embeddings to capture the surrounding context of sentences containing ESG-related terms to understand the specific goals or targets being referenced.
##    Temporal Relationship Understanding: Leverage contextual embeddings to capture the temporal relationship between statements and temporal expressions (e.g., "by 2025", "from 2025") to identify future targets and deadlines.
##    Impact Assessment: Utilize contextual embeddings to assess the potential impact of achieving ESG goals by analyzing the context of sentences discussing the anticipated outcomes or benefits.
##    Risk Identification: Analyze the context of sentences discussing potential challenges or risks associated with achieving ESG goals using contextual embeddings to identify areas requiring mitigation or intervention.
##    Comparative Analysis: Use contextual embeddings to compare the context of sentences discussing different ESG goals or targets within the same report or across multiple reports to identify trends or disparities.
## We can use these metrics/features and create a streamlit app. They have high quality templates we can use: https://streamlit.io/gallery





#One approach to contextual embeddings is the cosine similarity score where high score imply semantic similarity between the corresponding words, phrases, or sentences.
#Based on sample sentences, we can calculate similarity scores and find similar sentences. Its like carbon-sentence, gender-sentence etc but you can do more in-depth analysis.
import time
import psutil
from datetime import datetime
import requests
import pandas as pd
import spacy
import io
import re
import torch
from sentence_transformers import SentenceTransformer, util
from spacy.lang.en.stop_words import STOP_WORDS

# Load NLP model
nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Function to preprocess text
def preprocess(text):
    if not isinstance(text, str) or not text.strip():  # Ensure input is valid
        return "empty_text"  # Return placeholder text
    doc = nlp(text)
    tokens = [token.text for token in doc if token.text.lower() not in STOP_WORDS and not token.is_punct]
    return " ".join(tokens) if tokens else "empty_text"

# Function to calculate cosine similarity
def calculate_similarity(embedding1, embedding2):
    return util.pytorch_cos_sim(embedding1, embedding2)

# Function to compute similarity scores
def calculate_similarity_scores(new_comments, base_comments):
    new_comments_preprocessed = [preprocess(comment) for comment in new_comments]
    base_comments_preprocessed = [preprocess(comment) for comment in base_comments]
    
    if not new_comments_preprocessed or not base_comments_preprocessed:
        print("Warning: Empty input provided to similarity function.")
        return torch.tensor([])  # Return empty tensor if no valid input
    
    new_embeddings = model.encode(new_comments_preprocessed, convert_to_tensor=True)
    base_embeddings = model.encode(base_comments_preprocessed, convert_to_tensor=True)
    
    print("New embeddings shape:", new_embeddings.shape)
    print("Base embeddings shape:", base_embeddings.shape)
    
    if new_embeddings.shape[0] == 0 or base_embeddings.shape[0] == 0:
        print("Error: One of the embeddings is empty!")
        return torch.tensor([])
    
    similarity_matrix = calculate_similarity(new_embeddings, base_embeddings)
    avg_similarities = torch.mean(similarity_matrix, dim=1)  # Mean similarity score
    
    return avg_similarities

if __name__ == "__main__":
    start_time = datetime.now()
    
    df = pd.DataFrame({"Target sentence": [
        "first quarter 2023 financial results revenue was $134.3 million for the first quarter of 2023, a 17% increase from $114.5 million for the corresponding prior year period."
    ]})
    
    targetSentences = df['Target sentence'].to_list()
    intent = ["What are you working on this weekend?", "Are you building today?", "What are you building today?", "Hello builders, it's Saturday but we're still building."]
    
    similarity_scores = calculate_similarity_scores(targetSentences, intent)
    df["Similarity Score"] = similarity_scores.tolist()
    df.to_csv("Test_result.csv", index=False)
    
    stop_time = datetime.now()
    print(f"Time taken: {(stop_time - start_time).total_seconds()} seconds")
