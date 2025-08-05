import pytest

from app.core.graph.chains.generation import generation_chain
from app.core.graph.chains.hallucination_grader import (
    GradeHallucinations,
    hallucination_grader
)
from app.core.graph.chains.retrieval_grader import GradeDocuments, retrieval_grader
from app.core.graph.chains.router import RouteQuery, question_router
from app.core.graph.chains.answer_grader import GradeAnswer, answer_grader


class TestRetrievalGrader:
    """Test the retrieval grader chain."""

    def test_grades_relevant_document_as_yes(self, sample_question, sample_documents):
        """Test that relevant documents are graded as 'yes'."""
        doc_text = sample_documents[0].page_content

        result: GradeDocuments = retrieval_grader.invoke({
            "question": sample_question,
            "document": doc_text
        })

        assert result.binary_score == "yes"

    def test_grades_irrelevant_document_as_no(self, irrelevant_documents):
        """Test that irrelevant documents are graded as 'no'."""
        doc_text = irrelevant_documents[0].page_content

        result: GradeDocuments = retrieval_grader.invoke({
            "question": "agent memory",
            "document": doc_text
        })

        assert result.binary_score == "no"

    def test_handles_empty_document(self, sample_question):
        """Test behavior with empty document."""
        result: GradeDocuments = retrieval_grader.invoke({
            "question": sample_question,
            "document": ""
        })

        assert result.binary_score == "no"


class TestHallucinationGrader:
    """Test the hallucination grader chain."""

    def test_grounded_generation_passes(self, sample_question, sample_documents):
        """Test that grounded generation is marked as not hallucinated."""
        # Generate an answer using the documents
        generation = generation_chain.invoke({
            "context": sample_documents,
            "question": sample_question
        })

        result: GradeHallucinations = hallucination_grader.invoke({
            "documents": sample_documents,
            "generation": generation
        })

        assert result.binary_score is True

    def test_hallucinated_generation_fails(self, sample_documents):
        """Test that hallucinated content is detected."""
        hallucinated_text = "In order to make pizza we need to first start with the dough"

        result: GradeHallucinations = hallucination_grader.invoke({
            "documents": sample_documents,
            "generation": hallucinated_text
        })

        assert result.binary_score is False

    def test_handles_empty_generation(self, sample_documents):
        """Test behavior with empty generation."""
        result: GradeHallucinations = hallucination_grader.invoke({
            "documents": sample_documents,
            "generation": ""
        })

        assert result.binary_score is False


class TestQuestionRouter:
    """Test the question router chain."""

    @pytest.mark.parametrize("question,expected_route", [
        ("agent memory", "vectorstore"),
        ("prompt engineering techniques", "vectorstore"),
        ("adversarial attacks on LLMs", "vectorstore"),
        ("what is machine learning", "vectorstore"),
    ])
    def test_routes_ai_questions_to_vectorstore(self, question, expected_route):
        """Test that AI-related questions route to vectorstore."""
        result: RouteQuery = question_router.invoke({"question": question})
        assert result.datasource == expected_route

    @pytest.mark.parametrize("question,expected_route", [
        ("how to make pizza", "websearch"),
        ("current weather in New York", "websearch"),
        ("latest news about Tesla stock", "websearch"),
        ("best restaurants in Paris", "websearch"),
    ])
    def test_routes_general_questions_to_websearch(self, question, expected_route):
        """Test that general questions route to web search."""
        result: RouteQuery = question_router.invoke({"question": question})
        assert result.datasource == expected_route


class TestGenerationChain:
    """Test the generation chain."""

    def test_generates_answer_from_context(self, sample_question, sample_documents):
        """Test that generation chain produces reasonable output."""
        result = generation_chain.invoke({
            "context": sample_documents,
            "question": sample_question
        })

        assert isinstance(result, str)
        assert len(result) > 0
        assert "memory" in result.lower()  # Should mention memory for agent memory question

    def test_handles_empty_context(self, sample_question):
        """Test behavior with no context documents."""
        result = generation_chain.invoke({
            "context": [],
            "question": sample_question
        })

        assert isinstance(result, str)
        # Should still generate something, even without context

    def test_generation_includes_context_information(self, sample_documents):
        """Test that generated answer references provided context."""
        question = "What are the components of agent memory?"

        result = generation_chain.invoke({
            "context": sample_documents,
            "question": question
        })

        # Should reference concepts from the documents
        result_lower = result.lower()
        assert any(concept in result_lower for concept in ["short-term", "long-term", "vector", "storage"])


class TestAnswerGrader:
    """Test the answer grader chain."""

    def test_relevant_answer_passes(self, sample_question, sample_documents):
        """Test that answers addressing the question are graded as relevant."""
        # Generate a contextual answer
        generated_answer = generation_chain.invoke({
            "context": sample_documents,
            "question": sample_question
        })

        result: GradeAnswer = answer_grader.invoke({
            "question": sample_question,
            "generation": generated_answer
        })

        assert result.binary_score is True

    def test_irrelevant_answer_fails(self, sample_question):
        """Test that answers not addressing the question are graded as irrelevant."""
        irrelevant_answer = "Pizza is made with flour, water, yeast, and tomato sauce."

        result: GradeAnswer = answer_grader.invoke({
            "question": sample_question,
            "generation": irrelevant_answer
        })

        assert result.binary_score is False

    def test_partial_answer_evaluation(self):
        """Test grading of partially relevant answers."""
        question = "What are the key components of AI agent memory systems?"
        partial_answer = "Memory is important for AI systems to function properly."

        result: GradeAnswer = answer_grader.invoke({
            "question": question,
            "generation": partial_answer
        })

        # This should be graded as not fully addressing the specific question
        assert result.binary_score is False

    def test_comprehensive_answer_evaluation(self):
        """Test grading of comprehensive answers."""
        question = "What are the key components of AI agent memory systems?"
        comprehensive_answer = """AI agent memory systems consist of several key components:
        1. Short-term memory that uses the model's context window for immediate information
        2. Long-term memory that uses external vector databases for persistent storage
        3. Retrieval mechanisms to access relevant past information
        4. Memory management systems to organize and prioritize information"""

        result: GradeAnswer = answer_grader.invoke({
            "question": question,
            "generation": comprehensive_answer
        })

        assert result.binary_score is True

    def test_empty_answer_fails(self, sample_question):
        """Test that empty answers are graded as not addressing the question."""
        result: GradeAnswer = answer_grader.invoke({
            "question": sample_question,
            "generation": ""
        })

        assert result.binary_score is False

    def test_vague_answer_evaluation(self):
        """Test grading of vague, non-specific answers."""
        question = "How does semantic chunking improve RAG performance?"
        vague_answer = "It makes things better by improving the system performance."

        result: GradeAnswer = answer_grader.invoke({
            "question": question,
            "generation": vague_answer
        })

        # Vague answers should not be considered as properly addressing specific questions
        assert result.binary_score is False