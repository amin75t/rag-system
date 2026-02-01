"""
URL configuration for utils app.
"""
from django.urls import path
from .views import (
    test_api,
    convert_miladi_to_samci,
    convert_samci_to_miladi,
    alpha_chat_completion,
    alpha_embeddings
)
from .rag.views import (
    ChatView,
    AddDocumentsView,
    ChatHistoryView,
    SystemPromptView,
    HealthCheckView
)

app_name = 'utils'

urlpatterns = [
    path('test-api/', test_api, name='test_api'),
    path('miladi-to-samci/', convert_miladi_to_samci, name='miladi_to_samci'),
    path('samci-to-miladi/', convert_samci_to_miladi, name='samci_to_miladi'),
    path('alpha/chat/', alpha_chat_completion, name='alpha_chat_completion'),
    path('alpha/embeddings/', alpha_embeddings, name='alpha_embeddings'),
    
    # RAG Chat endpoints
    path('rag/chat/', ChatView.as_view(), name='rag_chat'),
    path('rag/documents/', AddDocumentsView.as_view(), name='rag_add_documents'),
    path('rag/history/', ChatHistoryView.as_view(), name='rag_history'),
    path('rag/system-prompt/', SystemPromptView.as_view(), name='rag_system_prompt'),
    path('rag/health/', HealthCheckView.as_view(), name='rag_health'),
]
