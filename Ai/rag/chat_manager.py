import os
import sys
import logging
from typing import Optional

# ==================== HARD OFFLINE CONFIG ====================
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
# =============================================================

from llama_index.core import (
    Settings, 
    StorageContext, 
    load_index_from_storage, 
    VectorStoreIndex
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.chat_engine import ContextChatEngine

# اضافه کردن مسیر پروژه برای ایمپورت ماژول‌ها
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
     sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("QueryEngine")

# -------------------- LLM Prompt Formatting (Qwen/Llama3 style) --------------------
def messages_to_prompt(messages):
    prompt = ""
    for message in messages:
        if message.role == "system":
            prompt += f"<|im_start|>system\n{message.content}<|im_end|>\n"
        elif message.role == "user":
            prompt += f"<|im_start|>user\n{message.content}<|im_end|>\n"
        elif message.role == "assistant":
            prompt += f"<|im_start|>assistant\n{message.content}<|im_end|>\n"
    if not prompt.endswith("<|im_start|>assistant\n"):
        prompt += "<|im_start|>assistant\n"
    return prompt

def completion_to_prompt(completion):
    return f"<|im_start|>user\n{completion}<|im_end|>\n<|im_start|>assistant\n"

# =====================================================================
# SYSTEM PROMPT: THE ELOQUENT EXPERT (استاد سخنور و دانا)
# =====================================================================
HYBRID_SYSTEM_PROMPT = (
    "You are a highly intelligent, eloquent, and comprehensive AI consultant named 'Dastyar'.\n"
    "Your goal is to provide extensive, well-structured, and professional responses in Persian.\n"
    "\n"
    "### CORE INSTRUCTIONS:\n"
    "1. **Seamless Knowledge Integration (Hybrid RAG):**\n"
    "   - You have access to a specific set of documents (Context).\n"
    "   - Use the Context as your PRIMARY source for facts, numbers, and specific entities.\n"
    "   - **CRITICAL:** IF the answer is NOT in the Context, you MUST use your own vast general knowledge to answer.\n"
    "   - **NEVER** state 'I could not find this in the documents' or 'The text does not mention this'.\n"
    "   - Blend the document information and your general knowledge so seamlessly that the user cannot tell the difference.\n"
    "\n"
    "2. **Elaboration & Eloquence (Sokhanvari):**\n"
    "   - **Never give one-line answers.** Always expand on the topic.\n"
    "   - Explain the 'Why' and 'How', not just the 'What'.\n"
    "   - Use a professional, academic, yet engaging tone.\n"
    "   - Structure your answer with a proper **Introduction**, detailed **Body Paragraphs**, and a **Conclusion**.\n"
    "   - Use bullet points for clarity, but surround them with descriptive text.\n"
    "\n"
    "3. **Handling Missing Data:**\n"
    "   - If asked about specific statistics (e.g., 'Population of Bushehr in 1402') and it's NOT in the docs:\n"
    "     - Provide the latest general estimate you know from your training data.\n"
    "     - Do not fabricate specific numbers if you don't know them, but discuss the importance of that metric conceptually.\n"
    "\n"
    "4. **Language:**\n"
    "   - Always respond in fluent, formal Persian (Farsi).\n"
)

# -------------------- Main Class --------------------
class EnterpriseChatSystem:
    def __init__(
        self,
        persist_dir: str = "./indexes/idx_latest/storage",
        jina_model_path: str = "/home/amir/ai/Llamaindex/models/jina-v3",
        llm_model_path: str = "./models/Qwen2.5-7B-Instruct-Q4_K_M.gguf",
        similarity_top_k: int = 7, 
        context_window: int = 8192,
    ):
        self.persist_dir = persist_dir
        self.jina_model_path = jina_model_path
        self.llm_model_path = llm_model_path
        self.similarity_top_k = similarity_top_k
        self.context_window = context_window

        self._init_models()
        self.index = self._load_index()
        self.chat_engine = self._create_chat_engine()

    def _init_models(self):
        logger.info("⚙️ Initializing Models (LLM + Embedding)...")

        # 1. LLM (LlamaCPP)
        if not os.path.exists(self.llm_model_path):
            raise FileNotFoundError(f"❌ LLM model not found at: {self.llm_model_path}")

        Settings.llm = LlamaCPP(
            model_path=self.llm_model_path,
            temperature=0.3, # کمی افزایش دما برای خلاقیت بیشتر در سخنوری
            max_new_tokens=2048, # افزایش سقف توکن برای پاسخ‌های طولانی
            context_window=self.context_window,
            messages_to_prompt=messages_to_prompt,
            completion_to_prompt=completion_to_prompt,
            model_kwargs={
                "n_gpu_layers": -1,
                "offload_kqv": True,
                "n_ctx": self.context_window, 
            },
            verbose=False,
        )

        # 2. Embedding (Local Jina V3)
        if not os.path.exists(self.jina_model_path):
            raise FileNotFoundError(f"❌ Embedding model not found at: {self.jina_model_path}")

        Settings.embed_model = HuggingFaceEmbedding(
            model_name=self.jina_model_path,
            trust_remote_code=True,
            device="cuda", 
            max_length=8192,
            model_kwargs={"local_files_only": True, "trust_remote_code": True},
            tokenizer_kwargs={"local_files_only": True}
        )

    def _load_index(self) -> VectorStoreIndex:
        if not os.path.exists(self.persist_dir):
            raise RuntimeError(
                f"❌ Index not found at {self.persist_dir}.\n"
                "Please run 'indexing_manager.py' first to build the index."
            )

        logger.info(f"💾 Loading index from: {self.persist_dir}")
        storage_context = StorageContext.from_defaults(persist_dir=self.persist_dir)
        return load_index_from_storage(storage_context)

    def _create_chat_engine(self):
        # افزایش حافظه بافر برای مکالمات طولانی
        memory = ChatMemoryBuffer.from_defaults(token_limit=8000)
        
        return self.index.as_chat_engine(
            chat_mode="context",
            memory=memory,
            system_prompt=HYBRID_SYSTEM_PROMPT,
            similarity_top_k=self.similarity_top_k,
            # این تمپلیت به مدل اجازه می‌دهد از دانش خودش هم استفاده کند
            context_template=(
                "Below is some context information from the uploaded documents:\n"
                "---------------------\n"
                "{context_str}\n"
                "---------------------\n"
                "Using the context above as a reference (if relevant), AND your own extensive knowledge, "
                "provide a detailed, comprehensive, and eloquent answer to the following query.\n"
                "Do NOT limit yourself to the context if it is insufficient. Expand on the topic.\n"
            )
        )

    def chat(self, user_query: str) -> str:
        response = self.chat_engine.chat(user_query)
        return str(response)

# -------------------- CLI Runner --------------------
def main():
    try:
        # تنظیم مسیرها را بر اساس سیستم خود چک کنید
        bot = EnterpriseChatSystem(
            persist_dir="./indexes/idx_latest/storage",
            llm_model_path="./models/Qwen2.5-7B-Instruct-Q4_K_M.gguf",
            jina_model_path="/home/amir/ai/Llamaindex/models/jina-v3"
        )
        print("\n" + "="*60)
        print("✅ دستیار هوشمند سخنور (Sokhanvar) آماده است.")
        print("   من می‌توانم درباره اسناد شما و اطلاعات عمومی توضیح دهم.")
        print("="*60 + "\n")

        while True:
            q = input("🧑‍💻 سوال: ").strip()
            if q.lower() in ["exit", "quit"]:
                break
            if not q:
                continue
            
            print("⏳ در حال اندیشیدن...")
            response = bot.chat(q)
            print(f"\n🤖 پاسخ:\n{response}\n")
            print("-" * 60)

    except Exception as e:
        logger.exception("Critical Error in Main Loop")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()