import React, { useState, useRef, useEffect } from 'react';
import { chatService, ChatRequest, ChatResponse } from '../services/chatService';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  documents?: string[];
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [nResults, setNResults] = useState(5);
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(1000);
  const [showSettings, setShowSettings] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const chatRequest: ChatRequest = {
        query: inputText,
        n_results: nResults,
        temperature: temperature,
        max_tokens: maxTokens,
      };

      const response: ChatResponse = await chatService.sendMessage(chatRequest);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: `پاسخ بر اساس ${response.count} سند مرتبط پیدا شد.`,
        sender: 'assistant',
        timestamp: new Date(),
        documents: response.sample_documents,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: error instanceof Error ? error.message : 'خطا در ارسال پیام',
        sender: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-slate-50 to-sky-50/30 flex flex-col font-iransans" dir="rtl">
      {/* Header with busher-ui style */}
      <header className="relative overflow-hidden bg-gradient-to-l from-sky-700 via-sky-800 to-sky-900 text-white shadow-xl">
        {/* decorative circles */}
        <div className="pointer-events-none absolute -left-20 -top-20 h-64 w-64 rounded-full bg-white/5" />
        <div className="pointer-events-none absolute -bottom-16 left-1/3 h-48 w-48 rounded-full bg-sky-400/10" />
        <div className="pointer-events-none absolute -right-10 top-4 h-32 w-32 rounded-full bg-sky-300/8" />
        
        <div className="relative bg-white/10 backdrop-blur-sm border-b border-white/10 p-4">
          <div className="max-w-4xl mx-auto flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/15 backdrop-blur-sm">
                <svg className="h-7 w-7 text-sky-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-black tracking-tight text-white">دستیار هوشمند</h1>
                <p className="text-sm text-sky-100">از سیستم RAG برای پاسخ به سوالات خود استفاده کنید</p>
              </div>
            </div>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 rounded-xl bg-white/15 backdrop-blur-sm text-sky-200 hover:bg-white/25 transition-all"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      {/* Settings Panel with busher-ui style */}
      {showSettings && (
        <div className="bg-white/90 backdrop-blur-sm border-b border-neutral-200/70 p-4 animate-slide-up">
          <div className="max-w-4xl mx-auto">
            <div className="rounded-xl bg-gradient-to-r from-violet-50 to-sky-50 p-4 border border-violet-200/50">
              <h3 className="text-sm font-bold text-violet-800 mb-3 flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                </svg>
                تنظیمات پیشرفته
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-medium text-neutral-700 mb-2">
                    تعداد نتایج (n_results)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="20"
                    value={nResults}
                    onChange={(e) => setNResults(parseInt(e.target.value) || 5)}
                    className="w-full px-3 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-500 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-neutral-700 mb-2">
                    دما (temperature)
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="2"
                    step="0.1"
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value) || 0.7)}
                    className="w-full px-3 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-500 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-neutral-700 mb-2">
                    حداکثر توکن (max_tokens)
                  </label>
                  <input
                    type="number"
                    min="100"
                    max="4000"
                    step="100"
                    value={maxTokens}
                    onChange={(e) => setMaxTokens(parseInt(e.target.value) || 1000)}
                    className="w-full px-3 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-500 text-sm"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12 animate-fade-in">
              <div className="mx-auto w-16 h-16 bg-gradient-to-br from-sky-500 to-sky-600 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-200/70 shadow-lg max-w-md mx-auto">
                <h2 className="text-xl font-bold text-sky-900 mb-2">به دستیار هوشمند خوش آمدید</h2>
                <p className="text-neutral-600">سوال خود را در مورد اسناد موجود بپرسید</p>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-start' : 'justify-end'} animate-slide-up`}
              >
                <div
                  className={`max-w-3xl rounded-2xl px-4 py-3 shadow-sm transition-all hover:shadow-md ${
                    message.sender === 'user'
                      ? 'bg-gradient-to-l from-sky-600 to-sky-700 text-white'
                      : 'bg-white text-gray-800 border border-neutral-200/70'
                  }`}
                >
                  <p className="text-sm">{message.text}</p>
                  {message.documents && message.documents.length > 0 && (
                    <div className={`mt-3 pt-3 border-t ${
                      message.sender === 'user' ? 'border-sky-500' : 'border-neutral-200'
                    }`}>
                      <p className="text-xs font-semibold mb-2">اسناد مرتبط:</p>
                      <div className="space-y-1">
                        {message.documents.slice(0, 3).map((doc, index) => (
                          <div key={index} className={`text-xs p-2 rounded-lg ${
                            message.sender === 'user' ? 'bg-sky-500/30' : 'bg-sky-50'
                          }`}>
                            {doc.length > 100 ? `${doc.substring(0, 100)}...` : doc}
                          </div>
                        ))}
                        {message.documents.length > 3 && (
                          <p className="text-xs text-sky-600">
                            و {message.documents.length - 3} سند دیگر...
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                  <p className={`text-xs mt-2 opacity-70 ${
                    message.sender === 'user' ? 'text-sky-100' : 'text-neutral-500'
                  }`}>
                    {message.timestamp.toLocaleTimeString('fa-IR')}
                  </p>
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-end animate-slide-up">
              <div className="bg-white text-gray-800 border border-neutral-200/70 rounded-2xl px-4 py-3 shadow-sm">
                <div className="flex items-center space-x-2 space-x-reverse">
                  <div className="w-2 h-2 bg-sky-600 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-sky-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-sky-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <span className="text-sm">در حال پردازش...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area with busher-ui style */}
      <div className="bg-white/95 backdrop-blur-sm border-t border-neutral-200/70 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-3">
            <textarea
              ref={inputRef}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="سوال خود را اینجا بنویسید..."
              className="flex-1 px-4 py-3 border border-neutral-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-500 resize-none transition-all"
              rows={1}
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !inputText.trim()}
              className="px-6 py-3 bg-gradient-to-l from-sky-600 to-sky-700 hover:from-sky-700 hover:to-sky-800 text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-[1.01] shadow-lg"
            >
              {isLoading ? (
                <svg className="animate-spin h-5 w-5 border-b-2 border-white rounded-full" viewBox="0 0 24 24"></svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;