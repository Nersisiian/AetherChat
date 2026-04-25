from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import re

def faithfulness(answer: str, context: str) -> float:
    answer_words = set(answer.lower().split())
    context_words = set(context.lower().split())
    if not context_words:
        return 0.0
    return len(answer_words & context_words) / len(answer_words)

def rouge_l(reference: str, candidate: str) -> float:
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    scores = scorer.score(reference, candidate)
    return scores['rougeL'].fmeasure