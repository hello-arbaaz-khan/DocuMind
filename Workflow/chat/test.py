from unittest.mock import Mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.auth_manager.models import User
from apps.chat.models import ChatMessage, Conversation, ConversationDocument
from apps.documents.models import UploadedDocument

from Workflow.chat.processing import ChatQueryWorkflow
from RagCore.ErrorsHandle.exceptions import IntegrationError


class ChatQueryIntegrationTests(TestCase):
    """Test Django chat workflows with mocked AI dependencies."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="chat-test@example.com",
            password="test-password",
            display_name="Chat Test User",
        )

        cls.document = cls._create_mock_processed_document(
            cls.user,
            "document-one.pdf",
        )
        cls.document_two = cls._create_mock_processed_document(
            cls.user,
            "document-two.docx",
        )

    @staticmethod
    def _create_mock_processed_document(user, filename):
        """Create a processed document without running ingestion or embeddings."""
        extension = filename.rsplit(".", 1)[-1].lower()

        content_types = {
            "pdf": "application/pdf",
            "docx": (
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
        }

        uploaded_file = SimpleUploadedFile(
            filename,
            b"Mock document content for chat workflow tests.",
            content_type=content_types[extension],
        )

        return UploadedDocument.objects.create(
            user=user,
            name=filename,
            file=uploaded_file,
            file_type=extension,
            file_size=uploaded_file.size,
            is_processed=True,
        )

    @staticmethod
    def _create_conversation(user, documents):
        conversation = Conversation.objects.create(
            user=user,
            title="Multi-document test",
        )

        ConversationDocument.objects.bulk_create([
            ConversationDocument(
                conversation=conversation,
                document=document,
            )
            for document in documents
        ])

        return conversation

    @staticmethod
    def _build_mock_agent(*answers):
        """Return deterministic answers without calling an LLM."""
        agent = Mock()
        agent.run.side_effect = answers
        return agent

    def test_multi_document_chat_query(self):
        conversation = self._create_conversation(
            self.user,
            [self.document, self.document_two],
        )
        agent = self._build_mock_agent(
            "The documents contain information about two sample topics."
        )

        result = ChatQueryWorkflow(agent=agent).run(
            user=self.user,
            question="What are these documents about?",
            conversation_id=conversation.id,
        )

        self.assertEqual(
            result.answer,
            "The documents contain information about two sample topics.",
        )
        self.assertEqual(result.conversation_id, conversation.id)

        self.assertEqual(
            ChatMessage.objects.filter(conversation=conversation).count(),
            2,
        )

        self.assertEqual(
            list(
                conversation.documents.order_by("id").values_list(
                    "id",
                    flat=True,
                )
            ),
            [self.document.id, self.document_two.id],
        )

        agent.run.assert_called_once_with(
            "What are these documents about?",
            document_ids=[
                str(self.document.id),
                str(self.document_two.id),
            ],
            conversation_context="",
        )

    def test_follow_up_uses_conversation_history(self):
        conversation = self._create_conversation(
            self.user,
            [self.document, self.document_two],
        )
        agent = self._build_mock_agent(
            "The documents discuss two sample topics.",
            "Here is a more detailed explanation.",
        )
        workflow = ChatQueryWorkflow(agent=agent)

        first = workflow.run(
            user=self.user,
            question="What are these documents about?",
            conversation_id=conversation.id,
        )

        second = workflow.run(
            user=self.user,
            question="Can you explain that in more detail?",
            conversation_id=conversation.id,
        )

        self.assertTrue(first.answer)
        self.assertTrue(second.answer)

        self.assertEqual(
            ChatMessage.objects.filter(conversation=conversation).count(),
            4,
        )

        second_call = agent.run.call_args_list[1]

        self.assertEqual(
            second_call.kwargs["conversation_context"],
            (
                "User: What are these documents about?\n\n"
                "Assistant: The documents discuss two sample topics."
            ),
        )

        self.assertEqual(
            second_call.args[0],
            "Can you explain that in more detail?",
        )

    def test_user_cannot_query_another_users_conversation(self):
        conversation = self._create_conversation(
            self.user,
            [self.document, self.document_two],
        )

        other_user = User.objects.create_user(
            email="other-chat-test@example.com",
            password="test-password",
            display_name="Other User",
        )

        agent = self._build_mock_agent("This answer must never be generated.")

        with self.assertRaises(IntegrationError):
            ChatQueryWorkflow(agent=agent).run(
                user=other_user,
                question="Read these documents.",
                conversation_id=conversation.id,
            )

        agent.run.assert_not_called()

        self.assertEqual(
            ChatMessage.objects.filter(conversation=conversation).count(),
            0,
        )

    def test_empty_question_is_rejected(self):
        conversation = self._create_conversation(
            self.user,
            [self.document],
        )
        agent = self._build_mock_agent("Unused answer")

        with self.assertRaises(IntegrationError):
            ChatQueryWorkflow(agent=agent).run(
                user=self.user,
                question="   ",
                conversation_id=conversation.id,
            )

        agent.run.assert_not_called()

    def test_conversation_without_documents_is_rejected(self):
        conversation = Conversation.objects.create(
            user=self.user,
            title="Empty conversation",
        )
        agent = self._build_mock_agent("Unused answer")

        with self.assertRaises(IntegrationError):
            ChatQueryWorkflow(agent=agent).run(
                user=self.user,
                question="Summarize the documents.",
                conversation_id=conversation.id,
            )

        agent.run.assert_not_called()

    def test_unprocessed_document_is_rejected(self):
        conversation = self._create_conversation(
            self.user,
            [self.document],
        )

        UploadedDocument.objects.filter(
            pk=self.document.pk
        ).update(is_processed=False)

        agent = self._build_mock_agent("Unused answer")

        with self.assertRaises(IntegrationError):
            ChatQueryWorkflow(agent=agent).run(
                user=self.user,
                question="Summarize this document.",
                conversation_id=conversation.id,
            )

        agent.run.assert_not_called()

    def test_empty_agent_answer_is_rejected(self):
        conversation = self._create_conversation(
            self.user,
            [self.document],
        )
        agent = self._build_mock_agent("   ")

        with self.assertRaises(IntegrationError):
            ChatQueryWorkflow(agent=agent).run(
                user=self.user,
                question="Summarize this document.",
                conversation_id=conversation.id,
            )

        self.assertEqual(
            ChatMessage.objects.filter(conversation=conversation).count(),
            0,
        )