import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FileText, Search, RefreshCw, Database,
  CheckCircle2, AlertCircle, Send, Info,
  ChevronRight, Download
} from 'lucide-react';

interface RAGStats {
  indexed_files: number;
  total_chunks: number;
  supported_formats: string[];
}

interface SearchResult {
  content: string;
  metadata: {
    source: string;
  };
  score: number;
}

const RAGDashboard: React.FC = () => {
  const [stats, setStats] = useState<RAGStats | null>(null);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [indexing, setIndexing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/rag/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Failed to fetch RAG stats:', err);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/rag/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query, k: 4 })
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data.results);
      } else {
        setError('Грешка при търсенето. Моля, опитайте отново.');
      }
    } catch (err) {
      setError('Няма връзка с API сървъра.');
    } finally {
      setLoading(false);
    }
  };

  const handleReindex = async () => {
    setIndexing(true);
    try {
      const response = await fetch('/api/rag/reindex', { method: 'POST' });
      if (response.ok) {
        const data = await response.json();
        setStats(data.total_stats);
        alert(`Успешно индексирани ${data.new_files} нови файла (${data.new_chunks} чанка).`);
      }
    } catch (err) {
      console.error('Indexing failed:', err);
    } finally {
      setIndexing(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Database className="text-blue-400" />
            Интелигентна база знания (RAG)
          </h1>
          <p className="text-gray-400 mt-1">
            Извличане на информация и обучение на системата чрез корпоративни документи.
          </p>
        </div>
        <button
          onClick={handleReindex}
          disabled={indexing}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
            indexing
              ? 'bg-blue-600/50 text-white cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-900/20'
          }`}
        >
          <RefreshCw className={`w-4 h-4 ${indexing ? 'animate-spin' : ''}`} />
          {indexing ? 'Индексиране...' : 'Обнови индекса'}
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-slate-900/50 backdrop-blur-md border border-slate-800 p-4 rounded-xl"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/10 rounded-lg">
              <FileText className="text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Индексирани файлове</p>
              <p className="text-2xl font-bold text-white">{stats?.indexed_files || 0}</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-slate-900/50 backdrop-blur-md border border-slate-800 p-4 rounded-xl"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500/10 rounded-lg">
              <Database className="text-purple-400" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Общо текстови сегмента (Chunks)</p>
              <p className="text-2xl font-bold text-white">{stats?.total_chunks || 0}</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-slate-900/50 backdrop-blur-md border border-slate-800 p-4 rounded-xl"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-500/10 rounded-lg">
              <CheckCircle2 className="text-emerald-400" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Поддържани формати</p>
              <p className="text-xs font-mono text-emerald-400">
                {stats?.supported_formats.join(', ') || 'Зареждане...'}
              </p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Search Interface */}
      <div className="bg-slate-900/50 backdrop-blur-md border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="p-6">
          <form onSubmit={handleSearch} className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Попитайте системата за специфична информация от документите..."
              className="w-full bg-slate-950 border border-slate-700 text-white pl-12 pr-24 py-4 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all placeholder:text-gray-600"
            />
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" />
            <button
              type="submit"
              disabled={loading}
              className="absolute right-2 top-1/2 -translate-y-1/2 bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-lg font-medium transition-all disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              Търси
            </button>
          </form>

          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-4 p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg flex items-center gap-2"
            >
              <AlertCircle className="w-4 h-4" />
              {error}
            </motion.div>
          )}

          <div className="mt-8 space-y-6">
            <AnimatePresence mode="popLayout">
              {results.length > 0 ? (
                results.map((result, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="group bg-slate-950/50 border border-slate-800 p-5 rounded-xl hover:border-blue-500/50 transition-all shadow-sm"
                  >
                    <div className="flex items-start justify-between gap-4 mb-3">
                      <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 uppercase tracking-wider">
                        <FileText className="w-3.5 h-3.5" />
                        Източник: {result.metadata.source}
                      </div>
                      <div className="text-[10px] text-gray-500 font-mono">
                        Score: {result.score.toFixed(4)}
                      </div>
                    </div>
                    <p className="text-gray-300 text-sm leading-relaxed">
                      {result.content}
                    </p>
                    <div className="mt-4 flex items-center gap-4 text-xs">
                      <button className="text-gray-500 hover:text-white flex items-center gap-1.5 transition-colors">
                        <Download className="w-3.5 h-3.5" />
                        Преглед на документа
                      </button>
                    </div>
                  </motion.div>
                ))
              ) : !loading && query && (
                <div className="text-center py-12 text-gray-500">
                  <Info className="w-12 h-12 mx-auto mb-4 opacity-20" />
                  <p>Няма намерени резултати за вашето търсене.</p>
                </div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900/50 backdrop-blur-md border border-slate-800 p-6 rounded-2xl">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Info className="text-blue-400 w-5 h-5" />
            Как работи RAG?
          </h3>
          <ul className="space-y-3 text-sm text-gray-400">
            <li className="flex items-start gap-2">
              <ChevronRight className="w-4 h-4 text-blue-500 mt-0.5 shrink-0" />
              Добавете документи в директорията <code>backend/RAG/documents</code>.
            </li>
            <li className="flex items-start gap-2">
              <ChevronRight className="w-4 h-4 text-blue-500 mt-0.5 shrink-0" />
              Кликнете "Обнови индекса", за да трансформирате текста във векторни ембединги.
            </li>
            <li className="flex items-start gap-2">
              <ChevronRight className="w-4 h-4 text-blue-500 mt-0.5 shrink-0" />
              Системата използва FAISS и HuggingFace модели за семантично търсене.
            </li>
            <li className="flex items-start gap-2">
              <ChevronRight className="w-4 h-4 text-blue-500 mt-0.5 shrink-0" />
              AI моделите се обучават върху контекста от тези документи за по-точни отговори.
            </li>
          </ul>
        </div>

        <div className="bg-slate-900/50 backdrop-blur-md border border-slate-800 p-6 rounded-2xl">
          <h3 className="text-lg font-semibold text-white mb-4">Предстоящи актуализации</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-slate-950/50 border border-slate-800 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
                <span className="text-sm text-gray-300">OCR за сканирани PDF-и</span>
              </div>
              <span className="text-[10px] bg-yellow-500/10 text-yellow-500 px-2 py-0.5 rounded border border-yellow-500/20">Скоро</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-950/50 border border-slate-800 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                <span className="text-sm text-gray-300">Интеграция с OpenAI/Llama 3</span>
              </div>
              <span className="text-[10px] bg-blue-500/10 text-blue-500 px-2 py-0.5 rounded border border-blue-500/20">В процес</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RAGDashboard;
