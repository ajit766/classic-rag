'use client';

import { useChat } from 'ai/react';
import { Send, User, Bot, BookOpen } from 'lucide-react';
import { useRef, useEffect } from 'react';
import clsx from 'clsx';

export default function ChatInterface() {
    const { messages, input, handleInputChange, handleSubmit, isLoading, error } = useChat({
        api: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1/chat',
        onError: (err) => console.error("Chat error:", err),
    });

    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    return (
        <div className="flex flex-col h-screen max-w-4xl mx-auto bg-gray-50 dark:bg-gray-900 border-x border-gray-200 dark:border-gray-800 shadow-xl">
            {/* Header */}
            <header className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 sticky top-0 z-10">
                <div className="flex items-center gap-3">
                    <div className="bg-indigo-600 p-2 rounded-lg text-white">
                        <BookOpen size={24} />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-gray-900 dark:text-white">The Modern Sage</h1>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Modern Psychology meets Ancient Spirituality</p>
                    </div>
                </div>
            </header>

            {/* Messages */}
            <main className="flex-1 overflow-y-auto p-6 space-y-6">
                {error && (
                    <div className="p-4 bg-red-100 text-red-700 rounded-xl border border-red-200">
                        <strong>Error:</strong> {error.message}
                    </div>
                )}
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-center text-gray-500 space-y-4">
                        <Bot size={48} className="text-indigo-300" />
                        <p className="text-lg">Ask me anything about habits, mindset, or life's purpose.</p>
                        <div className="flex flex-wrap gap-2 justify-center">
                            <span className="px-3 py-1 bg-gray-200 dark:bg-gray-800 rounded-full text-xs">"How do I build better habits?"</span>
                            <span className="px-3 py-1 bg-gray-200 dark:bg-gray-800 rounded-full text-xs">"What is Dharma?"</span>
                            <span className="px-3 py-1 bg-gray-200 dark:bg-gray-800 rounded-full text-xs">"Why do I procrastinate?"</span>
                        </div>
                    </div>
                )}

                {messages.map((m) => (
                    <div
                        key={m.id}
                        className={clsx(
                            "flex gap-4 p-4 rounded-2xl max-w-[85%]",
                            m.role === 'user'
                                ? "ml-auto bg-indigo-600 text-white"
                                : "bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-100 shadow-sm"
                        )}
                    >
                        <div className={clsx("flex-shrink-0 mt-1", m.role === 'user' ? "text-indigo-200" : "text-indigo-500")}>
                            {m.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                        </div>
                        <div className="prose dark:prose-invert text-sm leading-relaxed whitespace-pre-wrap">
                            {m.content}
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex gap-4 p-4 max-w-[85%] bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
                        <div className="flex-shrink-0 mt-1 text-indigo-500">
                            <Bot size={20} className="animate-pulse" />
                        </div>
                        <div className="text-sm text-gray-400 italic">Thinking...</div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </main>

            {/* Input */}
            <footer className="p-4 bg-white dark:bg-gray-950 border-t border-gray-200 dark:border-gray-800 sticky bottom-0">
                <form onSubmit={handleSubmit} className="relative flex items-center">
                    <input
                        className="w-full p-4 pr-12 rounded-xl bg-gray-100 dark:bg-gray-800 border-none focus:ring-2 focus:ring-indigo-500 text-gray-900 dark:text-white placeholder-gray-500"
                        value={input}
                        onChange={handleInputChange}
                        placeholder="Type your question..."
                        disabled={isLoading}
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        className="absolute right-3 p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        <Send size={18} />
                    </button>
                </form>
            </footer>
        </div>
    );
}
