<<<<<<< HEAD
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

app_name = 'utils'

urlpatterns = [
    path('test-api/', test_api, name='test_api'),
    path('miladi-to-samci/', convert_miladi_to_samci, name='miladi_to_samci'),
    path('samci-to-miladi/', convert_samci_to_miladi, name='samci_to_miladi'),
    path('alpha/chat/', alpha_chat_completion, name='alpha_chat_completion'),
    path('alpha/embeddings/', alpha_embeddings, name='alpha_embeddings'),
]
=======
"""
URL configuration for utils app.
"""
from django.urls import path
from .views import (
    test_api,
    convert_miladi_to_samci,
    convert_samci_to_miladi,
    alpha_chat_completion,
    alpha_embeddings,
    rag_chat,
    rag_debug
)

app_name = 'utils'

urlpatterns = [
    path('test-api/', test_api, name='test_api'),
    path('miladi-to-samci/', convert_miladi_to_samci, name='miladi_to_samci'),
    path('samci-to-miladi/', convert_samci_to_miladi, name='samci_to_miladi'),
    path('alpha/chat/', alpha_chat_completion, name='alpha_chat_completion'),
    path('alpha/embeddings/', alpha_embeddings, name='alpha_embeddings'),
    path('rag/chat/', rag_chat, name='rag_chat'),
    path('rag/debug/', rag_debug, name='rag_debug'),
]
>>>>>>> f2082a2bb03dbfe62c62d1a3b6c4c3034bfe2794
